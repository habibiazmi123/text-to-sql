package main

import (
	"log"
	"time"

	"text-to-sql-backend/internal/config"
	"text-to-sql-backend/internal/handler"
	"text-to-sql-backend/internal/service"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	cfg := config.Load()

	db, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		log.Fatalf("failed to get underlying DB: %v", err)
	}
	sqlDB.SetMaxIdleConns(5)
	sqlDB.SetMaxOpenConns(20)
	sqlDB.SetConnMaxLifetime(time.Hour)

	healthHandler := handler.NewHealthHandler(db)
	queryService := service.NewQueryService(db, cfg)
	queryHandler := handler.NewQueryHandler(queryService)

	r := gin.Default()
	r.GET("/health", healthHandler.Check)
	r.POST("/api/v1/query", queryHandler.Query)

	log.Printf("Server starting on port %s", cfg.ServerPort)
	if err := r.Run(":" + cfg.ServerPort); err != nil {
		log.Fatalf("failed to start server: %v", err)
	}
}
