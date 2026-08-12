package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"text-to-sql-backend/internal/config"
	"text-to-sql-backend/internal/model"

	"gorm.io/gorm"
)

type QueryService struct {
	db     *gorm.DB
	cfg    *config.Config
	client *http.Client
}

func NewQueryService(db *gorm.DB, cfg *config.Config) *QueryService {
	return &QueryService{
		db:     db,
		cfg:    cfg,
		client: &http.Client{Timeout: 30 * time.Second},
	}
}

func (s *QueryService) ExecuteQuery(req model.QueryRequest) (*model.QueryResponse, error) {
	genReq, _ := json.Marshal(map[string]interface{}{"question": req.Question, "history": req.History})
	resp, err := s.client.Post(s.cfg.AIServiceURL+"/ai/generate-with-retry", "application/json", bytes.NewReader(genReq))
	if err != nil {
		return nil, fmt.Errorf("failed to call AI service: %w", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var genResult struct {
		Sql           string   `json:"sql"`
		Reasoning     string   `json:"reasoning"`
		TablesUsed    []string `json:"tables_used"`
		Confidence    float64  `json:"confidence"`
		IsValid       bool     `json:"is_valid"`
		ValidationErr string   `json:"validation_error"`
		RetriesUsed   int      `json:"retries_used"`
		NeedsClarify  bool     `json:"needs_clarify"`
		ClarifyText   string   `json:"clarify_text"`
	}
	json.Unmarshal(body, &genResult)

	if genResult.NeedsClarify {
		return &model.QueryResponse{
			Question:     req.Question,
			NeedsClarify: true,
			ClarifyText:  genResult.ClarifyText,
		}, nil
	}

	if !genResult.IsValid {
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
