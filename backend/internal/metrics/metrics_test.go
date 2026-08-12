package metrics

import (
	"strings"
	"testing"
)

func TestRenderCountersAndAverages(t *testing.T) {
	reg := New()
	reg.Inc(RequestsTotal)
	reg.Add(RetriesTotal, 2)
	reg.Observe(QueryLatencyMs, 100)
	reg.Observe(QueryLatencyMs, 300)

	out := reg.Render()

	for _, want := range []string{
		"text_to_sql_requests_total 1",
		"text_to_sql_retries_total 2",
		"text_to_sql_query_latency_ms_sum 400",
		"text_to_sql_query_latency_ms_count 2",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("expected metrics output to contain %q, got:\n%s", want, out)
		}
	}
}

func TestRenderSorted(t *testing.T) {
	reg := New()
	reg.Observe(LlmLatencyMs, 5)
	reg.Inc(SuccessTotal)

	out := reg.Render()
	successIdx := strings.Index(out, SuccessTotal+" ")
	llmIdx := strings.Index(out, LlmLatencyMs+"_sum")
	if successIdx == -1 || llmIdx == -1 {
		t.Fatalf("missing metrics, got:\n%s", out)
	}
	if successIdx > llmIdx {
		t.Errorf("expected sorted output, got counters after averages:\n%s", out)
	}
}
