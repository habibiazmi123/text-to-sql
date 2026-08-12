package model

import "time"

type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type QueryRequest struct {
	Question string        `json:"question" binding:"required"`
	History  []ChatMessage `json:"history"`
}

type QueryResponse struct {
	ID            string      `json:"id"`
	Question      string      `json:"question"`
	SQL           string      `json:"sql"`
	Reasoning     string      `json:"reasoning"`
	TablesUsed    []string    `json:"tables_used"`
	Result        interface{} `json:"result"`
	Answer        string      `json:"answer"`
	ExecutionTime int64       `json:"execution_time_ms"`
	RowsReturned  int         `json:"rows_returned"`
	NeedsClarify  bool        `json:"needs_clarify"`
	ClarifyText   string      `json:"clarify_text"`
}

type QueryRecord struct {
	ID            string    `json:"id" gorm:"primaryKey"`
	Question      string    `json:"question"`
	SQL           string    `json:"sql"`
	Reasoning     string    `json:"reasoning"`
	TablesUsed    string    `json:"tables_used"`
	Answer        string    `json:"answer"`
	ExecutionTime int64     `json:"execution_time"`
	RowsReturned  int       `json:"rows_returned"`
	CreatedAt     time.Time `json:"created_at"`
}
