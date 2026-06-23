"""Unit tests for the deterministic scorer (no network, no server needed)."""

from mcpgauge.score import (
    WEIGHTS,
    grade_for,
    grade_rank,
    score_server,
    score_tool,
)

# Arrange: a well-defined tool and a poorly-defined one.
GOOD_TOOL = {
    "name": "list_pods",
    "description": (
        "List the pods in the cluster with their phase and restart count, "
        "unhealthy pods first. Returns a JSON array. Use after cluster_summary "
        "to enumerate workloads."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "description": "Restrict the listing to this namespace; empty lists all.",
            }
        },
    },
}

BAD_TOOL = {
    "name": "run",
    "description": "",
    "inputSchema": {
        "type": "object",
        "properties": {"x": {"type": "string"}},
    },
}


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def test_good_tool_outscores_bad_tool():
    good = score_tool(GOOD_TOOL["name"], GOOD_TOOL["description"], GOOD_TOOL["inputSchema"])
    bad = score_tool(BAD_TOOL["name"], BAD_TOOL["description"], BAD_TOOL["inputSchema"])
    assert good.score > bad.score
    assert good.grade in {"A", "B"}
    assert bad.grade in {"D", "F"}


def test_missing_description_scores_zero_purpose():
    bad = score_tool("run", "", {"type": "object", "properties": {}})
    assert bad.dimensions["purpose_clarity"] == 0.0
    assert "missing description" in bad.notes


def test_undocumented_parameters_flagged():
    result = score_tool(
        "query",
        "Run a SQL query and return rows.",
        {"type": "object", "properties": {"sql": {"type": "string"}}},
    )
    assert any("undocumented parameters" in n for n in result.notes)
    assert result.dimensions["parameter_semantics"] < 5.0


def test_no_params_gets_full_parameter_score():
    result = score_tool(
        "server_info",
        "Report the server's effective configuration as a JSON object.",
        {"type": "object", "properties": {}},
    )
    assert result.dimensions["parameter_semantics"] == 5.0


def test_generic_name_penalised_and_noted():
    result = score_tool(
        "run", "Do the thing and return output.", {"type": "object", "properties": {}}
    )
    assert result.dimensions["naming"] <= 2.0
    assert any("generic tool name" in n for n in result.notes)


def test_server_score_weights_minimum():
    # Two great tools and one terrible one: the min must drag the server down.
    tools = [GOOD_TOOL, GOOD_TOOL, BAD_TOOL]
    result = score_server(tools)
    assert result.tool_count == 3
    assert result.min_tool_score < result.mean_tool_score
    # server = 0.6*mean + 0.4*min, so it sits below the mean of the good tools.
    assert result.score < result.mean_tool_score + 1e-9


def test_empty_server_is_grade_f():
    result = score_server([])
    assert result.grade == "F"
    assert result.score == 0.0
    assert "no tools" in " ".join(result.notes)


def test_duplicate_tool_names_penalised():
    dup = dict(GOOD_TOOL)
    result = score_server([GOOD_TOOL, dup])
    assert any("duplicate tool names" in n for n in result.notes)


def test_grade_helpers_are_consistent():
    assert grade_for(4.5) == "A"
    assert grade_for(0.0) == "F"
    assert grade_rank("A") > grade_rank("B") > grade_rank("F")


def test_result_is_json_serialisable():
    import json

    result = score_server([GOOD_TOOL, BAD_TOOL])
    payload = json.dumps(result.to_dict())
    assert '"grade"' in payload
