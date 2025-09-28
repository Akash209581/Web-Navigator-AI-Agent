# New canonical module name for agents: web_erverywhere_agents
from . import web_agents  # type: ignore

# Re-export under the new name for compatibility
from web_agents import (
	annotate_all,
	stream_task_agent,
	search_google,
	collect_top_results,
	fetch_page_summary,
	is_pdf_url,
	stream_research_agent,
	stream_deep_research_agent,
	sse,
)
