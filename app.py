%%writefile app.py

# Import semuanya dulu
import streamlit as st
from bot import build_agent

st.set_page_config(
    page_title="Hydro Asisten",
    page_icon="🌱",
    layout="centered", # Mengubah tata letak agar lebih fokus
    initial_sidebar_state="collapsed"
)

# Judul
st.title("🌿 Hydro Asisten")
st.subheader("Asisten Pribadi untuk Pertumbuhan Hidroponik Anda")

# Session state untuk agent dan pesan
if "agent" not in st.session_state:
  st.session_state.agent = build_agent()
  # Pesan awal dari bot untuk memandu pengguna
  st.session_state.messages = [{
      "role": "assistant",
      "content": "Selamat datang! Saya Hydro Asisten. Saya bisa membantu Anda mengecek pH ideal, EC ideal, atau mendiagnosa daun kuning. Apa yang bisa saya bantu hari ini? Misalnya: 'pH ideal untuk selada' atau 'daun muda saya menguning'."
  }]

if "messages" not in st.session_state:
  # Ini hanya sebagai fallback, biasanya akan diisi di blok if "agent" not in st.session_state
  st.session_state.messages = []

agent = st.session_state.agent

# Tombol-tombol dan UI
reset_chat_button = st.button("🔄 Reset Chat")
if reset_chat_button:
  st.session_state.messages = []
  st.session_state.agent = build_agent()
  # user_input = None
  # ai_output = None


user_input = st.chat_input("Tanyakan sesuatu tentang hidroponik...")


for m in st.session_state.messages:
  with st.chat_message(m["role"]):
    st.markdown(m["content"], unsafe_allow_html=True)


if user_input is not None:
  # with st.chat_message("human"):
  st.session_state.messages.append({
    "role": "human",
    "content": user_input,
  })

  with st.chat_message("user"):
    st.markdown(user_input)


  with st.spinner("Thinking.."):
    ai_output = ""

    for step in agent.stream({"input": user_input}):
      if "actions" in step.keys():
        for action in step["actions"]:
          with st.chat_message("assistant"):
            tool_name = action.tool
            tool_input = action.tool_input

            tool_message = f"""
              <div style="border-left: 5px solid #4CAF50; padding:6px 10px; background-color: #f9f9f9; border-radius:4px; font-size:14px;">
                🛠️ <b>{tool_name}</b> <code>{tool_input}</code>
              </div>
            """
            st.session_state.messages.append({
              "role": "🛠️",
              "content": tool_message,
            })


            st.markdown(tool_message, unsafe_allow_html=True)


      if "output" in step.keys():
        ai_output = step["output"]


  with st.chat_message("assistant"):
    # with st.chat_message("assistant"):
    st.session_state.messages.append({
      "role": "assistant",
      "content": ai_output,
    })



    st.markdown(ai_output, unsafe_allow_html=True)


    # st.text(agent.memory.chat_memory.messages)
