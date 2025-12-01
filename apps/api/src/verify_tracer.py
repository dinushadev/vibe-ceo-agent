from src.adk_utils import AgentTracer

def verify_tracer():
    print("Verifying AgentTracer fix...")
    
    tracer = AgentTracer()
    
    # Check if get_executions exists
    if not hasattr(tracer, 'get_executions'):
        print("FAIL: get_executions method missing.")
        return
        
    # Test adding execution and retrieving it
    tracer.add_tool_execution("test_tool", {"arg": 1}, {"result": "ok"})
    
    executions = tracer.get_executions()
    
    if len(executions) == 1 and executions[0]["tool"] == "test_tool":
        print(f"Method get_executions called successfully. Result: {executions}")
        print("\nSUCCESS: Verification passed!")
    else:
        print(f"FAIL: Unexpected executions: {executions}")

if __name__ == "__main__":
    verify_tracer()
