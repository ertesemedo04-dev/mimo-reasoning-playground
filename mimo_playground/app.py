"""Gradio web UI for MiMo Reasoning Playground."""

import asyncio
import os
import json
import gradio as gr
from dotenv import load_dotenv

from .client import MiMoClient
from .challenges import CHALLENGES, get_categories, get_challenges

load_dotenv()

client = MiMoClient(
    api_base=os.getenv("MIMO_API_BASE", "https://api.xiaomi.com/v1"),
    api_key=os.getenv("MIMO_API_KEY", ""),
    model=os.getenv("MIMO_MODEL", "xmtp/mimo-v2.5-pro"),
)

# ── Preset system prompts for different reasoning modes ──
SYSTEM_PROMPTS = {
    "Default": "",
    "Step-by-Step": "Think step by step. Show your complete reasoning process before giving the final answer.",
    "Socratic": "Use the Socratic method. Ask yourself clarifying questions, challenge assumptions, and reason through contradictions before concluding.",
    "Adversarial": "First build the strongest possible argument FOR the premise. Then build the strongest AGAINST. Finally, synthesize both perspectives into a balanced conclusion.",
    "ELI5": "Explain your reasoning as if teaching a curious 10-year-old. Use simple analogies and concrete examples.",
    "Academic": "Reason with academic rigor. Cite relevant principles, define terms precisely, use formal logical structure, and acknowledge limitations.",
}


def format_reasoning_html(reasoning_text: str) -> str:
    """Format reasoning text into styled HTML blocks."""
    if not reasoning_text:
        return ""
    lines = reasoning_text.strip().split("\n")
    html_parts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Highlight step numbers
        if line[0].isdigit() and (line[1] in ".)" or (len(line) > 2 and line[1].isdigit() and line[2] in ".)")):
            html_parts.append(f'<div class="reasoning-step">🧠 {line}</div>')
        elif line.startswith(("- ", "* ", "• ")):
            html_parts.append(f'<div class="reasoning-detail">  ↳ {line[2:]}</div>')
        elif any(line.lower().startswith(kw) for kw in ["therefore", "thus", "so,", "hence", "in conclusion", "finally"]):
            html_parts.append(f'<div class="reasoning-conclusion">💡 {line}</div>')
        else:
            html_parts.append(f'<div class="reasoning-line">{line}</div>')
    return "\n".join(html_parts)


async def run_challenge(challenge_id: str, system_mode: str):
    """Run a selected challenge."""
    challenge = next((c for c in CHALLENGES if c.id == challenge_id), None)
    if not challenge:
        yield "", "", "Challenge not found", ""
        return

    system = SYSTEM_PROMPTS.get(system_mode, "")
    reasoning_html = ""
    answer_text = ""
    stats_text = "⏳ Streaming..."

    reasoning_raw = ""

    async for event in client.stream_reasoning(challenge.prompt, system=system):
        if event["type"] == "reasoning":
            reasoning_raw += event["content"]
            reasoning_html = format_reasoning_html(reasoning_raw)
            yield reasoning_html, answer_text, stats_text, reasoning_raw
        elif event["type"] == "answer":
            answer_text += event["content"]
            yield reasoning_html, answer_text, stats_text, reasoning_raw
        elif event["type"] == "done":
            data = event["data"]
            stats_text = (
                f"✅ Done | {data.model}\n"
                f"⏱️ {data.elapsed_ms:.0f}ms | "
                f"🎯 {data.tokens_used} tokens | "
                f"🧠 {len(data.reasoning_steps)} reasoning steps"
            )
            yield reasoning_html, answer_text, stats_text, reasoning_raw
        elif event["type"] == "error":
            stats_text = f"❌ Error: {event['message']}"
            yield reasoning_html, answer_text, stats_text, reasoning_raw


async def run_custom(prompt: str, system_mode: str, temperature: float, max_tokens: int):
    """Run a custom prompt."""
    if not prompt.strip():
        yield "", "", "Enter a prompt", ""
        return

    system = SYSTEM_PROMPTS.get(system_mode, "")
    reasoning_html = ""
    answer_text = ""
    stats_text = "⏳ Streaming..."
    reasoning_raw = ""

    async for event in client.stream_reasoning(prompt, system=system, temperature=temperature, max_tokens=max_tokens):
        if event["type"] == "reasoning":
            reasoning_raw += event["content"]
            reasoning_html = format_reasoning_html(reasoning_raw)
            yield reasoning_html, answer_text, stats_text, reasoning_raw
        elif event["type"] == "answer":
            answer_text += event["content"]
            yield reasoning_html, answer_text, stats_text, reasoning_raw
        elif event["type"] == "done":
            data = event["data"]
            stats_text = (
                f"✅ Done | {data.model}\n"
                f"⏱️ {data.elapsed_ms:.0f}ms | "
                f"🎯 {data.tokens_used} tokens | "
                f"🧠 {len(data.reasoning_steps)} reasoning steps"
            )
            yield reasoning_html, answer_text, stats_text, reasoning_raw
        elif event["type"] == "error":
            stats_text = f"❌ Error: {event['message']}"
            yield reasoning_html, answer_text, stats_text, reasoning_raw


def get_challenge_info(challenge_id: str) -> str:
    """Get challenge description."""
    challenge = next((c for c in CHALLENGES if c.id == challenge_id), None)
    if not challenge:
        return ""
    return f"**{challenge.title}** ({challenge.category} — {challenge.difficulty})\n\n{challenge.description}"


def build_ui():
    """Build the Gradio interface."""

    css = """
    .reasoning-step { padding: 8px 12px; margin: 4px 0; background: #1a1a2e;
        border-left: 3px solid #6c63ff; border-radius: 4px; color: #e0e0e0; }
    .reasoning-detail { padding: 4px 12px; margin: 2px 0; color: #a0a0a0;
        font-style: italic; }
    .reasoning-conclusion { padding: 8px 12px; margin: 4px 0; background: #1a2e1a;
        border-left: 3px solid #4caf50; border-radius: 4px; color: #c0ffc0; }
    .reasoning-line { padding: 4px 12px; margin: 2px 0; color: #d0d0d0; }
    """

    with gr.Blocks(
        title="MiMo Reasoning Playground",
        theme=gr.themes.Soft(
            primary_hue="indigo",
            neutral_hue="slate",
        ),
        css=css,
    ) as app:
        gr.Markdown(
            """
            # 🧠 MiMo Reasoning Playground
            ### Explore how Xiaomi's MiMo v2.5 Pro reasons through complex problems

            Watch the model's **chain-of-thought reasoning** unfold in real-time,
            then see the final answer emerge from the thinking process.
            """
        )

        with gr.Tabs():
            # ── Tab 1: Challenges ──
            with gr.Tab("🎯 Challenges"):
                with gr.Row():
                    with gr.Column(scale=1):
                        challenge_dropdown = gr.Dropdown(
                            choices=[(f"[{c.difficulty}] {c.title} — {c.category}", c.id) for c in CHALLENGES],
                            label="Select Challenge",
                            value=CHALLENGES[0].id,
                        )
                        challenge_info = gr.Markdown(get_challenge_info(CHALLENGES[0].id))
                        mode_select = gr.Radio(
                            choices=list(SYSTEM_PROMPTS.keys()),
                            label="Reasoning Mode",
                            value="Default",
                        )
                        run_btn = gr.Button("▶️ Run Challenge", variant="primary", size="lg")

                    with gr.Column(scale=2):
                        with gr.Accordion("🧠 Reasoning Trace (click to expand)", open=True):
                            reasoning_output = gr.HTML()
                            reasoning_raw = gr.Textbox(visible=False)  # for copy

                        answer_output = gr.Markdown(label="💡 Answer")
                        stats_output = gr.Textbox(label="📊 Stats", interactive=False)

                challenge_dropdown.change(get_challenge_info, challenge_dropdown, challenge_info)

                run_btn.click(
                    run_challenge,
                    [challenge_dropdown, mode_select],
                    [reasoning_output, answer_output, stats_output, reasoning_raw],
                )

            # ── Tab 2: Custom Prompt ──
            with gr.Tab("✏️ Custom"):
                with gr.Row():
                    with gr.Column(scale=1):
                        custom_prompt = gr.Textbox(
                            label="Your Prompt",
                            placeholder="Ask MiMo anything...",
                            lines=6,
                        )
                        custom_mode = gr.Radio(
                            choices=list(SYSTEM_PROMPTS.keys()),
                            label="Reasoning Mode",
                            value="Default",
                        )
                        with gr.Accordion("⚙️ Advanced", open=False):
                            temp_slider = gr.Slider(0, 2, 0.7, step=0.1, label="Temperature")
                            max_tok = gr.Slider(1024, 32768, 8192, step=1024, label="Max Tokens")
                        custom_btn = gr.Button("▶️ Run", variant="primary", size="lg")

                    with gr.Column(scale=2):
                        with gr.Accordion("🧠 Reasoning Trace", open=True):
                            c_reasoning = gr.HTML()
                            c_reasoning_raw = gr.Textbox(visible=False)
                        c_answer = gr.Markdown(label="💡 Answer")
                        c_stats = gr.Textbox(label="📊 Stats", interactive=False)

                custom_btn.click(
                    run_custom,
                    [custom_prompt, custom_mode, temp_slider, max_tok],
                    [c_reasoning, c_answer, c_stats, c_reasoning_raw],
                )

            # ── Tab 3: Compare Modes ──
            with gr.Tab("⚖️ Compare"):
                gr.Markdown(
                    """
                    ### Compare Reasoning Modes

                    Run the same prompt through different reasoning styles to see
                    how the thinking process changes.

                    Select a prompt and see side-by-side reasoning traces.
                    """
                )
                compare_prompt = gr.Textbox(
                    label="Prompt to compare",
                    placeholder="Enter a prompt to run through multiple reasoning modes...",
                    lines=4,
                )
                compare_btn = gr.Button("⚖️ Compare All Modes", variant="primary")
                compare_output = gr.Markdown(label="Comparison Results")

                async def run_comparison(prompt):
                    if not prompt.strip():
                        return "Enter a prompt first."
                    results = []
                    for mode_name in ["Step-by-Step", "Socratic", "Adversarial", "ELI5", "Academic"]:
                        system = SYSTEM_PROMPTS[mode_name]
                        reasoning_parts = []
                        answer_parts = []
                        async for event in client.stream_reasoning(prompt, system=system):
                            if event["type"] == "reasoning":
                                reasoning_parts.append(event["content"])
                            elif event["type"] == "answer":
                                answer_parts.append(event["content"])
                            elif event["type"] == "error":
                                results.append(f"### {mode_name}\n❌ {event['message']}")
                                break
                        else:
                            reasoning = "".join(reasoning_parts)[:500]
                            answer = "".join(answer_parts)
                            results.append(
                                f"### 🏷️ {mode_name}\n"
                                f"**Reasoning preview:** {reasoning}...\n\n"
                                f"**Answer:** {answer}\n\n---"
                            )
                    return "\n\n".join(results)

                compare_btn.click(run_comparison, compare_prompt, compare_output)

            # ── Tab 4: About ──
            with gr.Tab("ℹ️ About"):
                gr.Markdown(
                    """
                    ## About MiMo v2.5 Pro

                    **MiMo** (Xiaomi's Mi Model) is a reasoning-focused AI model
                    that exposes its chain-of-thought process through `reasoning_content`.

                    ### Key Features
                    - 🧠 **Explicit reasoning** — see every thinking step
                    - 📊 **Structured analysis** — breaks problems into components
                    - 🔄 **Self-correction** — catches and fixes its own mistakes
                    - 🎯 **Multi-modal reasoning** — logic, math, code, philosophy

                    ### How This Playground Works

                    1. **Challenges** — Pre-built problems designed to stress-test reasoning
                    2. **Custom** — Ask anything and watch the reasoning unfold
                    3. **Compare** — Run the same prompt through different reasoning modes

                    ### Reasoning Modes

                    | Mode | Description |
                    |------|-------------|
                    | Default | MiMo's natural reasoning style |
                    | Step-by-Step | Explicit sequential breakdown |
                    | Socratic | Self-questioning approach |
                    | Adversarial | Argues both sides before concluding |
                    | ELI5 | Simple explanations with analogies |
                    | Academic | Formal logical structure |

                    ### Tech Stack
                    - **Backend:** Python + httpx (async streaming)
                    - **UI:** Gradio
                    - **Model:** MiMo v2.5 Pro (Xiaomi)

                    ---

                    Built to explore reasoning model capabilities.
                    """
                )

    return app


def main():
    """Launch the playground."""
    app = build_ui()
    app.launch(
        server_name=os.getenv("HOST", "0.0.0.0"),
        server_port=int(os.getenv("PORT", "8501")),
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
