package metrics

import (
	"bytes"
	"fmt"
	"sort"
	"sync"
)

// Registry is a tiny thread-safe metrics store that renders Prometheus text
// format. Prometheus itself gathers from /metrics; adding the client_golang
// dependency buys nothing for a handful of in-process counters.
type Registry struct {
	mu       sync.Mutex
	counters map[string]float64
	averages map[string]*average
}

type average struct {
	sum   float64
	count float64
}

// Counter/metric names.
const (
	RequestsTotal      = "text_to_sql_requests_total"
	SuccessTotal       = "text_to_sql_success_total"
	ValidationFailed   = "text_to_sql_validation_failed_total"
	ExecutionFailed    = "text_to_sql_execution_failed_total"
	RetriesTotal       = "text_to_sql_retries_total"
	QueryLatencyMs     = "text_to_sql_query_latency_ms"
	RetrievalLatencyMs = "text_to_sql_retrieval_latency_ms"
	LlmLatencyMs       = "text_to_sql_llm_latency_ms"
	Tokens             = "text_to_sql_tokens"
)

// New returns an empty registry.
func New() *Registry {
	return &Registry{
		counters: map[string]float64{},
		averages: map[string]*average{},
	}
}

// Inc increments a counter by one.
func (r *Registry) Inc(name string) {
	r.mu.Lock()
	r.counters[name]++
	r.mu.Unlock()
}

// Add adds v to a counter.
func (r *Registry) Add(name string, v float64) {
	r.mu.Lock()
	r.counters[name] += v
	r.mu.Unlock()
}

// Observe records a value into a _sum/_count pair (for averages).
func (r *Registry) Observe(name string, v float64) {
	r.mu.Lock()
	a := r.averages[name]
	if a == nil {
		a = &average{}
		r.averages[name] = a
	}
	a.sum += v
	a.count++
	r.mu.Unlock()
}

// Render produces the Prometheus text exposition format.
func (r *Registry) Render() string {
	r.mu.Lock()
	defer r.mu.Unlock()

	var b bytes.Buffer
	counterNames := make([]string, 0, len(r.counters))
	for name := range r.counters {
		counterNames = append(counterNames, name)
	}
	sort.Strings(counterNames)
	for _, name := range counterNames {
		fmt.Fprintf(&b, "# TYPE %s counter\n%s %g\n", name, name, r.counters[name])
	}

	avgNames := make([]string, 0, len(r.averages))
	for name := range r.averages {
		avgNames = append(avgNames, name)
	}
	sort.Strings(avgNames)
	for _, name := range avgNames {
		a := r.averages[name]
		fmt.Fprintf(&b, "# TYPE %s_sum counter\n%s_sum %g\n", name, name, a.sum)
		fmt.Fprintf(&b, "# TYPE %s_count counter\n%s_count %g\n", name, name, a.count)
	}
	return b.String()
}
