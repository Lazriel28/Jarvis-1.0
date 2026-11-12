# Brave Search Setup for Jarvis

## What Was Implemented

Created `brave_search.py` - a proper Brave Search API integration for Jarvis that:
- Performs actual web searches via Brave's API
- Returns formatted results with titles, URLs, descriptions
- Includes AI summaries when available
- Handles errors gracefully
- Shows helpful setup instructions when no API key is configured

## Files Created/Modified

**New:**
- `src/jarvis/tools/builtin/brave_search.py` - Brave Search implementation

**Modified:**
- `src/jarvis/tools/builtin/jarvis_core.py` - jarvisInternet now uses Brave Search
- `src/jarvis/tools/registry.py` - Added braveSearch tool
- `src/jarvis/tools/builtin/__init__.py` - Exported BraveSearchTool

## How to Get a Brave Search API Key

1. **Go to:** https://brave.com/search/api/
2. **Sign up:** Create a free account
3. **Get API key:** Free tier includes 2,000 searches/month
4. **Copy your key:** It will look like `BSAT-...`

## How to Configure the API Key

**Option 1: Environment Variable (Recommended for testing)**
```powershell
# PowerShell - temporary (lasts until terminal closes)
$env:BRAVE_SEARCH_API_KEY="your-key-here"

# Or set permanently in Windows
setx BRAVE_SEARCH_API_KEY "your-key-here"
```

**Option 2: Config File (Future)**
Add to `~/.config/jarvis/config.json`:
```json
{
  "brave_search_api_key": "your-key-here"
}
```

**Option 3: .env file (if Jarvis supports it)**
Create `.env` in Jarvis working directory:
```
BRAVE_SEARCH_API_KEY=your-key-here
```

## Testing the Integration

Once you have a key configured:

1. **Restart Jarvis** (or the Python process using the tools)
2. **Use via voice:** "Jarvis, search for [topic]"
3. **Or test directly:**
```python
from jarvis.tools.builtin.brave_search import BraveSearchTool

tool = BraveSearchTool()
result = tool.run({"query": "latest AI news"}, None)
print(result.content[0]["text"])
```

## What Jarvis Can Do With Brave Search

- **Search the web** for current information
- **Get news** and articles
- **Research topics** with real search results
- **Find documentation** and technical info
- **Check facts** and get current data

## Pricing

- **Free tier:** 2,000 searches/month
- **Paid:** $5 per 1,000 additional requests
- **$5 free credit** every month

## Security Notes

- Never share your API key in chat or code
- Treat it like a password
- Rotate keys if compromised
- Use environment variables, not hardcoded values

## Troubleshooting

**"Brave Search Not Configured"**
- You haven't set the API key yet
- Follow setup instructions above

**"Search failed: 401 Unauthorized"**
- API key is invalid or expired
- Get a new key from Brave dashboard

**"Search failed: 429 Too Many Requests"**
- You've hit your rate limit
- Free tier: 0.2 requests/second initially
- Wait and try again, or upgrade plan

**"No module named 'requests'"**
- Install: `pip install requests`
- Jarvis should have this, but if not, install it

---

*With Brave Search configured, Jarvis will have real internet access for web searches.*
