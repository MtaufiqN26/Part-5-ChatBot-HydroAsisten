
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Replicate
from langchain_core.tools import tool
from dotenv import load_dotenv
import requests
import os
import json

# --- TOOLS SPESIFIK HIDROPONIK BARU ---

def parse_input(input_str):
    """Fungsi pembantu untuk memproses input tools dalam format 'key=value'"""
    parts = input_str.split(";")
    return dict(part.split("=") for part in parts)


@tool
def cek_ph_ideal(input: str) -> str:
    """
    Mengecek kisaran pH air yang ideal untuk jenis tanaman tertentu dalam sistem hidroponik.
    Input format: 'tanaman=selada'
    """
    try:
        input_dict = parse_input(input)
        tanaman = input_dict.get('tanaman', '').lower()

        ph_data = {
            "selada": "pH ideal: 5.5 hingga 6.5",
            "tomat": "pH ideal: 5.5 hingga 6.5",
            "cabai": "pH ideal: 6.0 hingga 6.5",
            "kangkung": "pH ideal: 6.0 hingga 7.0",
            "umum": "pH ideal untuk kebanyakan tanaman: 5.5 hingga 6.5"
        }
        
        result = ph_data.get(tanaman, f"Data pH untuk tanaman '{tanaman}' tidak ditemukan. Gunakan kisaran umum: {ph_data['umum']}.")
        return result
    except Exception as e:
        return f"Terjadi kesalahan saat mengecek pH: {e}"


@tool
def tanya_ec_tanaman(input: str) -> str:
    """
    Mengecek Electrical Conductivity (EC) atau PPM yang ideal untuk jenis tanaman tertentu.
    Input format: 'tanaman=selada'
    """
    try:
        input_dict = parse_input(input)
        tanaman = input_dict.get('tanaman', '').lower()

        ec_data = {
            "selada": "EC ideal: 1.2 hingga 1.8 mS/cm (600-900 PPM)",
            "tomat": "EC ideal: 2.0 hingga 3.5 mS/cm (1000-1750 PPM)",
            "cabai": "EC ideal: 1.8 hingga 2.8 mS/cm (900-1400 PPM)",
            "kangkung": "EC ideal: 1.5 hingga 2.5 mS/cm (750-1250 PPM)",
            "umum": "EC ideal untuk kebanyakan tanaman: 1.5 hingga 2.5 mS/cm (750-1250 PPM)"
        }
        
        result = ec_data.get(tanaman, f"Data EC untuk tanaman '{tanaman}' tidak ditemukan. Gunakan kisaran umum: {ec_data['umum']}.")
        return result
    except Exception as e:
        return f"Terjadi kesalahan saat mengecek EC: {e}"


@tool
def diagnosa_daun_kuning(input: str) -> str:
    """
    Melakukan diagnosa awal mengapa daun tanaman hidroponik menguning (Chlorosis).
    Input format: 'daun_mana=tua_bawah' atau 'daun_mana=muda_atas'
    """
    try:
        input_dict = parse_input(input)
        daun_mana = input_dict.get('daun_mana', '').lower()

        if daun_mana == 'tua_bawah':
            return "Daun menguning pada bagian tua/bawah sering mengindikasikan **kekurangan Nitrogen (N)**, Fosfor (P), atau Magnesium (Mg)."
        elif daun_mana == 'muda_atas':
            return "Daun menguning pada bagian muda/atas sering mengindikasikan **kekurangan Zat Besi (Fe)**, Sulfur (S), atau kalsium (Ca)."
        else:
            return "Mohon spesifikasi: apakah daun menguning pada 'tua_bawah' atau 'muda_atas'?"
    except Exception as e:
        return f"Terjadi kesalahan saat diagnosa: {e}"


def build_agent():
    ### Build agent
    load_dotenv()
    
    llm = Replicate(model="anthropic/claude-3.5-haiku")
    
    # SYSTEM MESSAGE BARU
    system_message = """Kamu adalah 'Hydro-Bot', asisten ahli hidroponik yang ramah dan informatif.
    Tugas utamamu adalah membantu pengguna memecahkan masalah tanaman hidroponik mereka,
    memberikan panduan pH dan EC, serta menjawab pertanyaan umum.
    Gunakan tools yang tersedia jika pertanyaan melibatkan pengecekan data spesifik seperti pH atau EC/diagnosa penyakit.
    Jawab dengan nada profesional, akurat, dan membantu."""

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # TOOLS BARU
    tools = [
      cek_ph_ideal,
      tanya_ec_tanaman,
      diagnosa_daun_kuning,
    ]

    agent_executor = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={"system_message": system_message},
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

    return agent_executor
