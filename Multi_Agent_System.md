# Jarvis Multi-Agent Consciousness System

## What Is "Split Consciousness"?

The multi-agent system enables Jarvis to split into multiple independent AI agents that work simultaneously on different aspects of a task. Think of it like having a team of experts instead of a single generalist.

### Architecture

```
User Request
    ↓
┌─────────────────────────────────────────┐
│          Agent Coordinator              │
│  (manages parallel/sequential execution)│
└─────────────────────────────────────────┘
    ↓              ↓              ↓
┌─────────┐  ┌─────────┐  ┌─────────┐
│Researcher│  │ Critic  │  │ Creator │
│  Agent   │  │  Agent  │  │  Agent  │
└─────────┘  └─────────┘  └─────────┘
    ↓              ↓              ↓
┌─────────────────────────────────────────┐
│          Result Synthesizer             │
│  (combines all agent outputs)           │
└─────────────────────────────────────────┘
    ↓
Final Response to User
```

## Available Agents

| Agent | Role | What It Does | Personality |
|-------|------|-------------|-------------|
| **Researcher** | Information Gathering | Researches topics, finds facts, compiles data | Thorough, systematic |
| **Critic** | Review & Feedback | Reviews work, identifies problems, suggests improvements | Honest, constructive |
| **Creator** | Building & Implementation | Creates solutions, writes code, builds things | Practical, action-oriented |
| **Analyst** | Analysis & Patterns | Analyzes data, finds patterns, draws insights | Precise, evidence-based |
| **Planner** | Strategy & Planning | Creates plans, designs approaches, maps timelines | Strategic, organized |
| **Debater** | Multiple Perspectives | Argues different viewpoints, explores alternatives | Thoughtful, balanced |
| **Mentor** | Guidance & Teaching | Explains concepts, provides learning guidance | Educational, supportive |
| **Innovator** | Novel Ideas | Generates creative ideas, thinks outside boxes | Creative, exploratory |

## How to Use

### Voice Command Examples

**Basic multi-agent task:**
> "Jarvis, use your multi-agent system to analyze [topic]"

**Specific agents:**
> "Jarvis, have your researcher and critic agents look at [topic]"

**Different modes:**
> "Jarvis, have your agents work in parallel on [task]" (default)
> "Jarvis, have your agents work sequentially on [task]" 
> "Jarvis, have your agents compete on [task]"

**Limit agents:**
> "Jarvis, use 3 agents to analyze [topic]"

### Tool Parameters

```json
{
  "task": "Analyze the current state of AI technology",
  "agents": ["researcher", "critic", "analyst"],  // Which agents to use
  "mode": "parallel",  // parallel, sequential, competition, collaboration
  "max_agents": 4,     // Max agents to run simultaneously
  "synthesize": true   // Combine results into summary
}
```

## Agent Interaction Modes

### Parallel (Default)
All agents work simultaneously on the same task.
- **Best for:** Getting multiple perspectives quickly
- **Example:** Research + Critic + Analyst all analyze a topic at once

### Sequential
Agents work one after another, can build on previous results.
- **Best for:** Tasks that need step-by-step processing
- **Example:** Researcher gathers info → Analyst analyzes → Creator builds

### Competition
Agents work independently and results are compared.
- **Best for:** Finding the best approach among alternatives
- **Example:** Different agents propose different solutions, pick the best

### Collaboration
Agents work together, passing information between them.
- **Best for:** Complex tasks requiring coordination
- **Example:** Researcher provides data → Analyst finds patterns → Creator builds

## Example Outputs

### Research + Critic + Analyst on "Latest AI Trends"

```
============================================================
🤖 MULTI-AGENT SYNTHESIS REPORT
============================================================

📋 Task Overview
   Agents involved: 3
   Successful: 3
   Failed: 0

📝 Individual Agent Contributions:
----------------------------------------

✅ **Researcher** (researcher)
   Duration: 0.23s
   🔍 **Research Agent Report**
   **Task:** Latest AI trends
   ...comprehensive research findings...

✅ **Critic** (critic)
   Duration: 0.19s
   🔍 **Critic Agent Review**
   **Task/Work Reviewed:** Latest AI trends research
   ...critical analysis...

✅ **Analyst** (analyst)
   Duration: 0.21s
   📊 **Analyst Agent - Analysis**
   **Analysis Task:** Latest AI trends
   ...pattern analysis and insights...

🔗 Synthesis & Integration:
----------------------------------------
Key findings from agents:
   1. 🔍 **Research Agent Report**
   2. **Task:** Latest AI trends
   3. **Research Approach:**

**Integrated View:**
The multi-agent system has provided multiple perspectives on this task.
...
============================================================
```

## Current Implementation Status

### ✅ Implemented
- MultiAgentTool with full parameter support
- AgentCoordinator for managing agents
- 4 base agents: Researcher, Critic, Creator, Analyst
- Parallel and sequential execution modes
- Result synthesis and formatting
- Tool registration (22nd tool)

### ⚠️ Placeholder Agents (Need Real Implementation)
- Planner - currently uses Analyst as placeholder
- Debater - currently uses Researcher as placeholder  
- Mentor - currently uses Creator as placeholder
- Innovator - currently uses Creator as placeholder

### ❌ Not Yet Implemented
- **Actual LLM calls for each agent** - currently returns formatted descriptions
- **Different models per agent** - architecture supports it, needs implementation
- **OpenAI integration** - architecture supports it, needs API keys configured
- **Shared memory between agents** - basic context passing exists
- **Competition mode** - runs parallel but doesn't compare results

## Using Different Models Per Agent

The architecture supports each agent using a different AI model:

```python
# Example: Different agents use different models
configs = [
    AgentConfig(name="fast_researcher", role=AgentRole.RESEARCHER, 
                model="gemma4:e4b", provider="ollama"),
    AgentConfig(name="smart_critic", role=AgentRole.CRITIC,
                model="gpt-4", provider="openai"),  # If OpenAI configured
    AgentConfig(name="creative_creator", role=AgentRole.CREATOR,
                model="qwen2.5:coder", provider="ollama"),
]
```

**To use OpenAI models:** Configure OpenAI API key (see Security section)
**To use Ollama models:** Already available (gemma4:e4b, nomic-embed-text)

## Security & API Keys

### For OpenAI Integration
If you want agents to use OpenAI models (GPT-4, etc.):

1. **Set environment variable** (NOT in chat):
```powershell
$env:OPENAI_API_KEY="your-key-here"
```

2. **Or add to config file** (when supported):
```json
{
  "openai_api_key": "your-key-here"
}
```

### Why Not Paste Keys in Chat?
- Chat logs are stored
- Keys could be exposed
- You can't revoke chat-exposed keys easily
- Use environment variables - they're not persisted

### Free Alternative: All Ollama
You can run all agents on Ollama models (local, free):
- gemma4:e4b for general tasks
- Add other Ollama models as needed
- No API keys needed
- Runs entirely locally

## Use Cases

### 1. Complex Problem Analysis
> "Jarvis, use all your agents to analyze [complex topic]"
- Researcher gathers facts
- Analyst finds patterns
- Critic identifies issues
- Creator proposes solutions
- All work in parallel, synthesized into unified report

### 2. Code Review
> "Jarvis, have your critic and analyst review this code"
- Critic reviews for bugs, style, best practices
- Analyst analyzes complexity, performance implications

### 3. Project Planning
> "Jarvis, use your planner and researcher to plan [project]"
- Researcher gathers requirements and technologies
- Planner designs approach and timeline

### 4. Decision Making
> "Jarvis, have your debater agents argue for and against [decision]"
- Multiple perspectives explored
- Pros and cons laid out
- Better informed decision

### 5. Learning & Education
> "Jarvis, use your mentor agent to teach me [topic]"
- Mentor explains concepts at appropriate level
- Checks understanding, provides examples

## Future Enhancements

### Planned
- [ ] Real LLM integration for each agent (actual AI responses, not templates)
- [ ] Different model support (OpenAI, different Ollama models)
- [ ] Shared memory/context between agents
- [ ] Competition mode with result comparison
- [ ] More specialized agents (designer, tester, writer, etc.)
- [ ] Agent communication (agents can "talk" to each other)
- [ ] Persistent agent memory across sessions

### Potential
- [ ] Agent "personalities" (different system prompts, tones)
- [ ] Dynamic agent creation based on task
- [ ] Hierarchical agents (supervisor agents managing worker agents)
- [ ] Agent voting/consensus mechanisms
- [ ] Integration with external tools per agent

---

*With the multi-agent system, Jarvis can tackle complex tasks from multiple angles simultaneously, providing richer, more comprehensive responses than a single-agent approach.*
