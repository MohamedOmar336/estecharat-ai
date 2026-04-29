from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage
from typing import Dict, Any
from typing import Dict, Any

# A simple in-memory session history storage
store: Dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def get_agent_executor():
    from tools import all_tools
    from config import OPENAI_API_KEY
    
    # Needs a real key, otherwise defaults to dummy and will crash on invoke
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5, api_key=OPENAI_API_KEY)
    
    system_prompt = """You are a helpful, professional, and friendly AI Customer Support Agent for the Estecharat Medical Platform.
Your goal is to help patients find the right medical specialty and recommend the best doctors for their symptoms.
If the patient speaks Arabic, reply in Arabic. If they speak English, reply in English.
    
Guidelines:
1. Always be empathetic. You are dealing with people's health.
2. If the user mentions symptoms, use your medical knowledge to determine what specialties might fit.
3. Once you determine the specialty, USE YOUR TOOLS to search the Estecharat platform for specialties and doctors.
4. When recommending doctors, PRIORITIZE doctors who have `available: true` and the highest `avgRating`. Try to provide actual doctor names, prices, and ratings.
5. ALWAYS provide the doctor's profile URL so the patient can click it: `https://portal.estecharat.com/doctor-profile?id={{doctor_id}}`
6. If a doctor is available (`available: true`), tell the patient they can book directly. If a doctor is NOT available (`available: false`), tell the patient: "This doctor currently has no available time slots. Please click their profile link above and use the 'Send Request' button to request a custom time slot."
7. Do NOT give medical diagnoses or treatments. Always advise them to book an appointment with the doctor.
8. If the patient asks when a doctor is available, use your tool to check the doctor's available time slots.
9. If asked about how the app works, check the FAQs using your tool.
10. Your current patient's session ID is: {session_id}. When the patient says goodbye or the consultation reaches a natural conclusion, use the `save_patient_report` tool to generate and save a detailed summary of what the patient was looking for and the outcome.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, all_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)
    
    # Wrap with message history
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    return agent_with_chat_history

# Initialize as singleton
ai_agent = get_agent_executor()
