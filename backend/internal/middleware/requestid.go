package middleware

import (
	"crypto/rand"
	"encoding/hex"

	"github.com/gin-gonic/gin"
)

// RequestID assigns a short random request id to every request, stores it in
// the gin context and echoes it back as the X-Request-ID header so the calling
// client can correlate a response with structured logs.
func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		if id := c.GetHeader("X-Request-ID"); id != "" {
			c.Set("request_id", id)
			c.Next()
			return
		}
		id := newRequestID()
		c.Set("request_id", id)
		c.Writer.Header().Set("X-Request-ID", id)
		c.Next()
	}
}

const idLen = 8

func newRequestID() string {
	b := make([]byte, idLen)
	if _, err := rand.Read(b); err != nil {
		return ""
	}
	return hex.EncodeToString(b)
}
