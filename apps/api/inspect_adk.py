
import inspect
from google.adk.sessions import InMemorySessionService

service = InMemorySessionService()
print("get_session signature:", inspect.signature(service.get_session))
print("create_session signature:", inspect.signature(service.create_session))
print("Is get_session async?", inspect.iscoroutinefunction(service.get_session))
