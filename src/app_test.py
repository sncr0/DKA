import streamlit as st

# Initialize button_count in session state if it doesn't exist.
if "button_count" not in st.session_state:
    st.session_state.button_count = 1

def add_button():
    # Increment the count, which will cause a new button to appear on the next rerun.
    st.session_state.button_count += 1

st.write("Click any button to add a new button:")

# Loop over the number of buttons stored in session state.
for i in range(st.session_state.button_count):
    # Create each button with a unique key.
    if st.button(f"Button {i+1}", key=f"btn_{i}"):
        st.write(f"Button {i+1} clicked!")
        add_button()  # This updates the count; on the next rerun, one extra button will be shown.
        st.rerun()
