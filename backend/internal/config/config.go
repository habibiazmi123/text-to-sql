package config

import "os"

type Config struct {
	DatabaseURL  string
	AIServiceURL string
	ServerPort   string
}

func Load() *Config {
	return &Config{
		DatabaseURL:  getEnv("DATABASE_URL", "postgres://app_user:app_password@localhost:5432/text_to_sql?sslmode=disable"),
		AIServiceURL: getEnv("AI_SERVICE_URL", "http://localhost:8000"),
		ServerPort:   getEnv("SERVER_PORT", "8080"),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
