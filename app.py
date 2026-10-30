import streamlit as st
import joblib
import numpy as np

st.set_page_config(page_title="PhishGuard AI", page_icon="🛡️")

@st.cache_resource
def load_model():
    return joblib.load("models/phishguard.pkl")

model = load_model()
tfidf = model.named_steps["tfidf"]
clf = model.named_steps["clf"]
words = np.array(tfidf.get_feature_names_out())

st.title("🛡️ PhishGuard AI")
st.write("Paste an email below to get a phishing risk estimate and see why.")

subject = st.text_input("Subject (optional)")
body = st.text_area("Email body", height=250)

if st.button("Analyze"):
    text = (subject + " " + body).strip()

    if len(body.strip()) < 20:
        st.warning("Please paste a longer email body (at least 20 characters).")
    else:
        vec = tfidf.transform([text])
        prob = clf.predict_proba(vec)[0][1]
        pct = prob * 100

        st.subheader("Result")
        st.metric("Phishing risk estimate", f"{pct:.1f}%")
        st.progress(float(prob))

        if pct >= 70:
            st.error("High risk: this email looks like phishing.")
        elif pct >= 30:
            st.warning("Medium risk: be careful with this email.")
        else:
            st.success("Low risk: this email looks legitimate.")

        contrib = vec.toarray()[0] * clf.coef_[0]
        top_phish = [i for i in np.argsort(contrib)[-8:][::-1] if contrib[i] > 0]
        top_safe = [i for i in np.argsort(contrib)[:8] if contrib[i] < 0]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Pushes toward phishing")
            if top_phish:
                for i in top_phish:
                    st.write(f"- **{words[i]}**")
            else:
                st.write("No strong phishing signals.")
        with col2:
            st.subheader("Pushes toward safe")
            if top_safe:
                for i in top_safe:
                    st.write(f"- **{words[i]}**")
            else:
                st.write("No strong safe signals.")

        st.caption("This is a risk estimate, not proof that an email is malicious. "
                   "Legitimate emails can look suspicious and phishing emails can evade detection.")
