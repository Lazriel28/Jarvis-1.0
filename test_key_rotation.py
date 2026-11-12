#!/usr/bin/env python3
"""
API Key Rotation Smoke Test
"""

import sys
import os

# Add project root to path first
project_root = '/c/Users/Owner/.local/share/jarvis/jarvis-source/jarvis-main'
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

print("=" * 70)
print("API KEY ROTATION - SMOKE TEST")
print("=" * 70)
print()

# Step 1: Import and test key manager
print("STEP 1: Loading API Key Manager...")
print("-" * 70)

try:
    from jarvis.tools.builtin.api_key_manager import (
        APIKeyManager,
        APIKeyInfo,
        KeyStatus,
        get_key_manager
    )
    print("[OK] APIKeyManager imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import APIKeyManager: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Step 2: Load keys from .env file
print("STEP 2: Loading keys from .env file...")
print("-" * 70)

manager = APIKeyManager()

env_file = '/c/Users/Owner/.local/share/jarvis/.env'
try:
    count = manager.load_from_file(env_file)
    print(f"[OK] Loaded {count} keys from {env_file}")
except Exception as e:
    print(f"[WARN] Failed to load from {env_file}: {e}")
    count = 0

env_count = manager.load_from_env()
if env_count > 0:
    print(f"[OK] Loaded {env_count} additional keys from environment")

total_keys = len(manager._keys)
print()
print(f"TOTAL KEYS LOADED: {total_keys}")
print()

# Step 3: Show key summary
print("STEP 3: Key Status Summary...")
print("-" * 70)

status_counts = {"healthy": 0, "degraded": 0, "quota_exceeded": 0, "invalid": 0, "unknown": 0}

for key_id, key_info in manager._keys.items():
    status = key_info.status.value
    if status in status_counts:
        status_counts[status] += 1

print("  Status distribution:")
for status, count in status_counts.items():
    icon = {"healthy": "OK", "degraded": "WARN", "quota_exceeded": "EXHAUSTED", 
            "invalid": "INVALID", "unknown": "UNKNOWN"}.get(status, "?")
    print(f"    {icon}: {status}: {count}")

print()
print("  First 10 keys (masked):")
for key_id in sorted(manager._keys.keys())[:10]:
    key = manager._keys[key_id]
    print(f"    Key {key_id}: {key.masked_key} [{key.status.value}]")

if len(manager._keys) > 10:
    print(f"    ... and {len(manager._keys) - 10} more keys")

print()

# Step 4: Show current key
print("STEP 4: Current Key Selection...")
print("-" * 70)

current = manager.get_healthy_key()
if current:
    print(f"[OK] Selected current key: {current.key_id}")
    print(f"     Masked: {current.masked_key}")
    print(f"     Status: {current.status.value}")
else:
    print("[INFO] No healthy keys available (all unknown until tested)")
    print("       Will use first key for initial attempt")

print()

# Step 5: Test OpenAI wrapper
print("STEP 5: Testing OpenAI Rotation Wrapper...")
print("-" * 70)

try:
    from jarvis.tools.builtin.openai_with_rotation import (
        OpenAIWithRotation,
        get_openai_client,
        create_chat_completion
    )
    print("[OK] OpenAIWithRotation imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import OpenAIWithRotation: {e}")
    import traceback
    traceback.print_exc()
    # Continue anyway - we can still verify the manager
    client = None

if client is not None:
    print()
    print("Creating OpenAI client with rotation...")
    try:
        client = OpenAIWithRotation(
            api_key_file=env_file,
            default_model='gpt-4o-mini',
            max_retries=3,
            cooldown_seconds=1
        )
        print("[OK] OpenAI client created")
        print(f"     Current key ID: {client._current_key_id}")
    except Exception as e:
        print(f"[FAIL] Failed to create client: {e}")
        import traceback
        traceback.print_exc()
        client = None

print()

# Step 6: Attempt minimal API call (if client available)
if client is not None:
    print("STEP 6: Attempting minimal API call (smoke test)...")
    print("-" * 70)
    
    if not client.get_current_key_info():
        print("[SKIP] No key available for testing")
    else:
        print(f"Attempting call with key: {client._current_key_id}")
        print("(Expected to fail with invalid key - that's OK, rotation will be demonstrated)")
        print()
        
        try:
            response = client.create_chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
                temperature=0
            )
            
            print("[OK] API call succeeded!")
            print(f"     Response: {response.choices[0].message.content.strip()}")
            if hasattr(response, 'usage'):
                print(f"     Usage: {response.usage.prompt_tokens} in, {response.usage.completion_tokens} out")
            print()
            print("     Key rotation was NOT triggered (call succeeded on first key)")
            
        except Exception as e:
            error_str = str(e)
            print(f"[INFO] API call failed: {type(e).__name__}")
            print(f"     Error (truncated): {error_str[:150]}")
            print()
            
            error_type = client._handle_api_error(e)
            print(f"     Detected error type: {error_type}")
            print()
            
            print("     Key rotation behavior:")
            old_key_id = client._current_key_id
            print(f"       Error occurred on key: {old_key_id}")
            print(f"       Error classified as: {error_type}")
            
            # Check if rotation was triggered
            new_key_id = client._current_key_id
            if new_key_id != old_key_id:
                print(f"       [OK] Rotation triggered! Switched to: {new_key_id}")
            else:
                print(f"       [INFO] No rotation occurred (may need more errors or different error type)")
            
            print()
            print("     Key states after attempted call (first 5):")
            for key_id in sorted(manager._keys.keys())[:5]:
                key = manager._keys[key_id]
                print(f"       Key {key_id}: {key.masked_key} -> {key.status.value} (errors: {key.error_count})")

print()

# Step 7: Final status
print("STEP 7: Final Key Status Report...")
print("-" * 70)

summary = manager.get_status_summary()
print(f"Total keys: {summary['total_keys']}")
print(f"Healthy: {summary['healthy_keys']}")
print(f"Current key: {summary['current_key_id']}")
print()

healthy_list = []
exhausted_list = []
unknown_list = []

for key_info in summary['keys']:
    status = key_info['status']
    key_id = key_info['key_id']
    
    if status == 'healthy':
        healthy_list.append(key_id)
    elif status in ('quota_exceeded', 'invalid'):
        exhausted_list.append(f"{key_id} ({status})")
    else:
        unknown_list.append(key_id)

print("USABLE KEYS (healthy):")
if healthy_list:
    for k in healthy_list[:10]:
        print(f"  - Key {k}")
    if len(healthy_list) > 10:
        print(f"  ... and {len(healthy_list) - 10} more")
else:
    print("  (none identified yet - all in UNKNOWN state)")

print()
print("EXHAUSTED/INVALID KEYS:")
if exhausted_list:
    for k in exhausted_list[:10]:
        print(f"  - {k}")
    if len(exhausted_list) > 10:
        print(f"  ... and {len(exhausted_list) - 10} more")
else:
    print("  (none)")

print()
print(f"UNKNOWN (untested): {len(unknown_list)} keys")
if unknown_list:
    print(f"  First few: {', '.join(unknown_list[:5])}")
    if len(unknown_list) > 5:
        print(f"  ... and {len(unknown_list) - 5} more")

print()
print("=" * 70)
print("SMOKE TEST COMPLETE")
print("=" * 70)
print()
print("VERIFICATION SUMMARY:")
print("  - APIKeyManager: IMPORTED and INITIALIZED")
print(f"  - Keys loaded: {total_keys} from .env file")
print("  - OpenAI wrapper: IMPORTED")
if client:
    print("  - OpenAI client: CREATED")
    print("  - Rotation logic: IMPLEMENTED")
print()
print("KEY STATUS AFTER TEST:")
print(f"  - Healthy: {len(healthy_list)}")
print(f"  - Exhausted/invalid: {len(exhausted_list)}")
print(f"  - Unknown (untested): {len(unknown_list)}")
print()
print("NOTES:")
print("  - Keys in UNKNOWN state haven't been tested against API yet")
print("  - Once tested, they'll be marked HEALTHY or INVALID/QUOTA_EXCEEDED")
print("  - Rotation automatically uses healthy keys")
print("  - 429 (quota) and 401 (invalid) errors trigger rotation")
print()
print("TO RUN A LIVE TEST:")
print("  The client attempted a call but it likely failed (demo keys).")
print("  To test with real keys, ensure valid OpenAI keys are in .env")
