package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"time"

	"text-to-sql-backend/internal/config"
	"text-to-sql-backend/internal/metrics"
	"text-to-sql-backend/internal/model"

	"gorm.io/gorm"
)

type QueryService struct {
	db     *gorm.DB
	cfg    *config.Config
	client *http.Client
	reg    *metrics.Registry
	log    *slog.Logger
}

func NewQueryService(db *gorm.DB, cfg *config.Config, reg *metrics.Registry, log *slog.Logger) *QueryService {
	return &QueryService{
		db:     db,
		cfg:    cfg,
		client: &http.Client{Timeout: 30 * time.Second},
		reg:    reg,
		log:    log,
	}
}

// aiGenerateResponse mirrors the fields returned by the Python /ai/generate-with-retry
// endpoint relevant to Go, including the aggregated observability fields.
type aiGenerateResponse struct {
	Sql           string   `json:"sql"`
	Reasoning     string   `json:"reasoning"`
	TablesUsed    []string `json:"tables_used"`
	Confidence    float64  `json:"confidence"`
	IsValid       bool     `json:"is_valid"`
	ValidationErr string   `json:"validation_error"`
	RetriesUsed   int      `json:"retries_used"`
	NeedsClarify  bool     `json:"needs_clarify"`
	ClarifyText   string   `json:"clarify_text"`
	RetrievalMs   int64    `json:"retrieval_ms"`
	LlmMs         int64    `json:"llm_ms"`
	TokensUsed    int      `json:"tokens_used"`
}

func (s *QueryService) ExecuteQuery(req model.QueryRequest, requestID string) (*model.QueryResponse, error) {
	reg := s.reg
	reg.Inc(metrics.RequestsTotal)

	genReq, _ := json.Marshal(map[string]interface{}{"question": req.Question, "history": req.History})
	if req.History == nil {
		genReq, _ = json.Marshal(map[string]interface{}{"question": req.Question, "history": []model.ChatMessage{}})
	}
	resp, err := s.client.Post(s.cfg.AIServiceURL+"/ai/generate-with-retry", "application/json", bytes.NewReader(genReq))
	if err != nil {
		reg.Inc(metrics.ExecutionFailed)
		s.log.Error("ai_service_call_failed", "request_id", requestID, "error", err.Error())
		return nil, fmt.Errorf("failed to call AI service: %w", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var genResult aiGenerateResponse
	json.Unmarshal(body, &genResult)

	if genResult.NeedsClarify {
		s.log.Info("query_clarify_requested", "request_id", requestID, "question", req.Question, "clarify_text", genResult.ClarifyText)
		return &model.QueryResponse{
			Question:     req.Question,
			NeedsClarify: true,
			ClarifyText:  genResult.ClarifyText,
		}, nil
	}

	if !genResult.IsValid {
		reg.Inc(metrics.ValidationFailed)
		reg.Add(metrics.RetriesTotal, float64(genResult.RetriesUsed))
		reg.Observe(metrics.RetrievalLatencyMs, float64(genResult.RetrievalMs))
		reg.Observe(metrics.LlmLatencyMs, float64(genResult.LlmMs))
		reg.Observe(metrics.Tokens, float64(genResult.TokensUsed))
		s.log.Warn("query_validation_failed",
			"request_id", requestID,
			"question", req.Question,
			"sql", genResult.Sql,
			"validation_error", genResult.ValidationErr,
			"retries_used", genResult.RetriesUsed,
			"llm_ms", genResult.LlmMs,
			"retrieval_ms", genResult.RetrievalMs,
			"tokens", genResult.TokensUsed,
		)
		return &model.QueryResponse{
			Question:  req.Question,
			SQL:       genResult.Sql,
			Reasoning: fmt.Sprintf("Validation failed after %d retries: %s", genResult.RetriesUsed, genResult.ValidationErr),
		}, fmt.Errorf("SQL validation failed after %d retries: %s", genResult.RetriesUsed, genResult.ValidationErr)
	}

	start := time.Now()
	var result []map[string]interface{}
	queryErr := s.db.Raw(genResult.Sql).Scan(&result).Error
	execTime := time.Since(start).Milliseconds()

	if queryErr != nil {
		reg.Inc(metrics.ExecutionFailed)
		s.log.Error("query_execution_failed",
			"request_id", requestID,
			"question", req.Question,
			"sql", genResult.Sql,
			"error", queryErr.Error(),
			"llm_ms", genResult.LlmMs,
			"retrieval_ms", genResult.RetrievalMs,
			"tokens", genResult.TokensUsed,
		)
		return nil, fmt.Errorf("query execution failed: %w", queryErr)
	}

	rowsReturned := len(result)

	sumReq, _ := json.Marshal(map[string]interface{}{
		"question": req.Question,
		"sql":      genResult.Sql,
		"result":   result,
	})
	sumResp, err := s.client.Post(s.cfg.AIServiceURL+"/ai/summarize", "application/json", bytes.NewReader(sumReq))
	if err != nil {
		reg.Add(metrics.RetriesTotal, float64(genResult.RetriesUsed))
		reg.Observe(metrics.QueryLatencyMs, float64(execTime))
		reg.Observe(metrics.RetrievalLatencyMs, float64(genResult.RetrievalMs))
		reg.Observe(metrics.LlmLatencyMs, float64(genResult.LlmMs))
		reg.Observe(metrics.Tokens, float64(genResult.TokensUsed))
		s.log.Warn("query_summarize_skipped",
			"request_id", requestID,
			"question", req.Question,
			"sql", genResult.Sql,
			"error", err.Error(),
			"execution_ms", execTime,
			"rows_returned", rowsReturned,
		)
		return &model.QueryResponse{
			SQL:           genResult.Sql,
			Result:        result,
			RowsReturned:  rowsReturned,
			ExecutionTime: execTime,
		}, nil
	}
	defer sumResp.Body.Close()

	sumBody, _ := io.ReadAll(sumResp.Body)
	var sumResult struct {
		Answer string `json:"answer"`
	}
	json.Unmarshal(sumBody, &sumResult)

	reg.Inc(metrics.SuccessTotal)
	reg.Add(metrics.RetriesTotal, float64(genResult.RetriesUsed))
	reg.Observe(metrics.QueryLatencyMs, float64(execTime))
	reg.Observe(metrics.RetrievalLatencyMs, float64(genResult.RetrievalMs))
	reg.Observe(metrics.LlmLatencyMs, float64(genResult.LlmMs))
	reg.Observe(metrics.Tokens, float64(genResult.TokensUsed))

	s.log.Info("query_success",
		"request_id", requestID,
		"question", req.Question,
		"sql", genResult.Sql,
		"tables_used", genResult.TablesUsed,
		"execution_ms", execTime,
		"rows_returned", rowsReturned,
		"retries_used", genResult.RetriesUsed,
		"exec_answer_ok", sumResult.Answer != "",
		"llm_ms", genResult.LlmMs,
		"retrieval_ms", genResult.RetrievalMs,
		"tokens", genResult.TokensUsed,
	)

	return &model.QueryResponse{
		Question:      req.Question,
		SQL:           genResult.Sql,
		Reasoning:     genResult.Reasoning,
		TablesUsed:    genResult.TablesUsed,
		Result:        result,
		Answer:        sumResult.Answer,
		ExecutionTime: execTime,
		RowsReturned:  rowsReturned,
	}, nil
}
