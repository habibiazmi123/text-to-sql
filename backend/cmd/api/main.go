package main

import (
	"log/slog"
	"os"
	"time"

	"text-to-sql-backend/internal/config"
	"text-to-sql-backend/internal/handler"
	"text-to-sql-backend/internal/metrics"
	"text-to-sql-backend/internal/middleware"
	"text-to-sql-backend/internal/service"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	cfg := config.Load()

	db, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		logger.Error("failed to connect to database", "error", err.Error())
		os.Exit(1)
	}

	sqlDB, err := db.DB()
	if err != nil {
		logger.Error("failed to get underlying DB", "error", err.Error())
		os.Exit(1)
	}
	sqlDB.SetMaxIdleConns(5)
	sqlDB.SetMaxOpenConns(20)
	sqlDB.SetConnMaxLifetime(time.Hour)

	reg := metrics.New()
	healthHandler := handler.NewHealthHandler(db)
	queryService := service.NewQueryService(db, cfg, reg, logger)
	queryHandler := handler.NewQueryHandler(queryService)

	r := gin.New()
	r.Use(middleware.RequestID())
	r.GET("/health", healthHandler.Check)
	r.POST("/api/v1/query", queryHandler.Query)
	r.GET("/metrics", func(c *gin.Context) {
		c.String(200, reg.Render())
	})

	logger.Info("server starting", "port", cfg.ServerPort)
	if err := r.Run(":" + cfg.ServerPort); err != nil {
		logger.Error("failed to start server", "error", err.Error())
		os.Exit(1)
	}
}
