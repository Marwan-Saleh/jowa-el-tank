
import os
import html
import streamlit as st
import requests

API_BASE_URL = os.getenv(
    "JOW_API_BASE_URL",
    "https://chapter-nearly-twisty.ngrok-free.dev",
).rstrip("/")
API_KEY = os.getenv("JOW_API_KEY", "")

headers = {"X-API-Key": API_KEY} if API_KEY else {}

st.set_page_config(
    page_title="جوا التانك 🦈 | دخل فكرتك التانك",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Visual system ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');
    :root {
        --gold:#e8bb67;
        --gold2:#f5d99b;
        --ink:#080e18;
        --panel:#101a29;
        --muted:#aab6c8;
    }
    html, body, [class*="css"] {
        font-family:'Cairo', sans-serif;
    }
    .stApp {
        background:radial-gradient(
            ellipse at 78% 0%, #263044 0%,
            #101827 34%, #080d15 78%
        );
        color:#f7f4ed;
    }
    [data-testid="stHeader"] { background:rgba(0,0,0,0); }
    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,#0b121e,#070b12);
        border-right:1px solid #273246;
    }
    [data-testid="stSidebar"] * { color:#edf1f8; }
    .brand {
        font-weight:900;
        font-size:2rem;
        line-height:1.1;
        color:var(--gold2);
    }
    .tagline {
        color:#aab6c8;
        margin-top:.25rem;
        font-size:.92rem;
    }
    .eyebrow {
        color:var(--gold);
        font-size:.78rem;
        letter-spacing:2px;
        font-weight:800;
    }
    .hero {
        padding:1.5rem 1.7rem;
        border:1px solid #344057;
        border-radius:22px;
        background:linear-gradient(
            120deg,rgba(25,38,57,.97),rgba(10,16,26,.96)
        );
        box-shadow:0 18px 55px #0005;
        margin-bottom:1.2rem;
    }
    .hero h1 {
        margin:.2rem 0;
        font-size:clamp(1.8rem,3vw,2.8rem);
        color:#fff7e8;
    }
    .hero p { color:#b9c4d5; margin:.35rem 0 0; }
    .panel {
        background:rgba(14,22,35,.9);
        border:1px solid #29364b;
        border-radius:18px;
        padding:1.1rem 1.2rem;
    }
    .shark-name {
        font-weight:900;
        font-size:1.1rem;
        color:var(--gold2);
        margin-top:.35rem;
    }
    .shark-role { color:#aab6c8; font-size:.83rem; }
    .question-box {
        background:linear-gradient(120deg,#281d2a,#171b29);
        border:1px solid #6b4352;
        border-radius:18px;
        padding:1.2rem 1.35rem;
        font-size:1.15rem;
        line-height:1.9;
        color:#fff8ee;
        margin:1rem 0;
    }
    .stButton > button[kind="primary"] {
        background:linear-gradient(110deg,#e8bb67,#f2d79c);
        color:#111827;
        border:0;
        border-radius:12px;
        font-weight:900;
        min-height:2.8rem;
    }
    .stButton > button { border-radius:12px; }
    div[data-testid="stTextArea"] textarea {
        background:#0b1320;
        color:#f5f6fa;
        border:1px solid #344057;
        border-radius:12px;
    }
    [data-testid="stMetric"] {
        background:#101a29;
        padding:1rem;
        border:1px solid #29364b;
        border-radius:14px;
    }
    hr { border-color:#29364b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Investor information ----------
AVATARS = {
    "Mahmoud": {
        "name": "الحاج عمران",
        "role": "خبير المال والاستثمار",
        "emoji": "🧔🏽",
        "portrait": "👳🏽‍♂️",
        "description": "صعيدي صاحب خبرة في الفلوس والحسابات",
        "colors": "#c99446",
    },
    "Mona": {
        "name": "مدام منى",
        "role": "خبيرة التسويق والعملاء",
        "emoji": "🎯",
        "portrait": "👩🏻‍💼",
        "description": "تركّز على السوق واحتياجات العملاء",
        "colors": "#e77776",
    },
    "Sherif": {
        "name": "مستر شريف",
        "role": "خبير التنفيذ والتشغيل",
        "emoji": "⚙️",
        "portrait": "👨🏻‍💼",
        "description": "يركّز على التنفيذ والخطوات العملية",
        "colors": "#81a9f8",
    },
    "Manal": {
        "name": "أستاذة منال",
        "role": "خبيرة المخاطر والاستدامة",
        "emoji": "🛡️",
        "portrait": "👩🏻‍💼",
        "description": "تراجع المخاطر والحلول البديلة",
        "colors": "#bd91f4",
    },
}

NAME_ALIASES = {
    "الحاج عمران": "Mahmoud",
    "مدام منى": "Mona",
    "مستر شريف": "Sherif",
    "أستاذة منال": "Manal",
    "استاذة منال": "Manal",
}


def resolve_speaker(raw_name):
    raw_name = str(raw_name or "").strip()

    if raw_name in AVATARS:
        return raw_name

    if raw_name in NAME_ALIASES:
        return NAME_ALIASES[raw_name]

    lowered = raw_name.lower()

    for key, info in AVATARS.items():
        if key.lower() in lowered or info["name"] in raw_name:
            return key

    return None


def api_request(method, path, **kwargs):
    kwargs.setdefault("timeout", 60)

    response = requests.request(
        method,
        f"{API_BASE_URL}{path}",
        headers=headers,
        **kwargs,
    )

    response.raise_for_status()
    return response.json()


def get_active_speaker(data):
    question = data.get("question", {}) or {}
    return resolve_speaker(question.get("speaker", ""))


def render_shark_card(key, active=False, compact=False):
    shark = AVATARS[key]

    with st.container(border=True):
        col1, col2 = st.columns(
            [1, 2.2] if compact else [1, 2]
        )

        with col1:
            font_size = "2.2rem" if compact else "3.3rem"

            st.markdown(
                f"<div style='font-size:{font_size};"
                f"text-align:center;line-height:1.4'>"
                f"{shark['portrait']}</div>",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"<div class='shark-name'>{shark['name']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='shark-role'>{shark['role']}</div>",
                unsafe_allow_html=True,
            )

            if active:
                st.caption("🎙️ الدور الحالي")
            elif not compact:
                st.caption(shark["description"])


# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">اختبار الأفكار على أصوله</div>
      <h1>🦈 جوا التانك</h1>
      <p>دخل فكرتك التانك وشوف هتطلع منه عايشة ولا لأ.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(
        "<div class='brand'>جوا التانك 🦈</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='tagline'>"
        "دخل فكرتك التانك وشوف هتطلع منه عايشة ولا لأ."
        "</div>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("### مراحل الرحلة")
    st.markdown("🟡 مقابلات المستثمرين")
    st.markdown("⚪ تقييم المشروع")
    st.markdown("⚪ القرار النهائي")
    st.divider()

    with st.expander("إعدادات الاتصال", expanded=False):
        st.caption("API endpoint")
        st.code(API_BASE_URL, language=None)

        if st.button("اختبار الاتصال", use_container_width=True):
            try:
                health = api_request("GET", "/health")
                st.success("الاتصال شغال")
                st.json(health)
            except Exception as exc:
                st.error(f"فشل الاتصال: {exc}")

    if st.button("＋ جلسة جديدة", use_container_width=True):
        st.session_state.pop("session_data", None)
        st.session_state.pop("answer_draft", None)
        st.rerun()


# ---------- Create a session ----------
st.markdown(
    "<div class='eyebrow'>ابدأ رحلتك</div>",
    unsafe_allow_html=True,
)
st.subheader("احكي لنا عن مشروعك")

idea = st.text_area(
    "فكرة المشروع",
    placeholder=(
        "مثال: تطبيق بيربط الطباخين اللي بيعملوا أكل بيتي "
        "بالعملاء في منطقتهم..."
    ),
    height=115,
    key="idea_input",
)

if st.button(
    "🚀 ابدأ مقابلات المستثمرين",
    type="primary",
    use_container_width=True,
):
    if not idea.strip():
        st.warning("اكتب فكرة المشروع الأول.")
    else:
        try:
            with st.spinner("بنجهّز قاعة المستثمرين..."):
                data = api_request(
                    "POST",
                    "/sessions",
                    json={"idea": idea.strip()},
                    timeout=120,
                )

            st.session_state["session_data"] = data
            st.session_state.pop("answer_draft", None)
            st.rerun()

        except requests.RequestException as exc:
            st.error(f"مش قادر أوصل للـ API: {exc}")
        except Exception as exc:
            st.error(f"حصل خطأ: {exc}")


# ---------- Main interview experience ----------
if "session_data" in st.session_state:
    data = st.session_state["session_data"]
    session_id = data.get("session_id")
    question = data.get("question", {}) or {}

    raw_speaker = question.get("speaker", "")
    active_key = get_active_speaker(data)
    active = AVATARS.get(active_key) if active_key else None

    # These phases come from the backend.
    phase = data.get("phase", "interview")
    is_final_ready = phase in ("final_ready", "complete")

    st.divider()
    left, right = st.columns([1.55, 1], gap="large")

    with left:
        st.markdown("### 🎙️ المقابلة الحالية")

        if is_final_ready:
            st.success("انتهت مقابلات المستثمرين الأربعة!")
            st.info(
                "تقدر تنتقل دلوقتي لمرحلة تقييم المشروع والقرار النهائي."
            )

        elif active:
            render_shark_card(active_key, active=True)

            st.markdown(
                "<div class='question-box' dir='rtl'>"
                f"{html.escape(str(question.get('message', '')))}"
                "</div>",
                unsafe_allow_html=True,
            )

            answer = st.text_area(
                "إجابتك للمستثمر",
                key=f"answer_{session_id}",
                placeholder="اكتب إجابتك هنا... خليك واضح ومحدد.",
                height=135,
            )

            if st.button(
                "إرسال الإجابة ←",
                type="primary",
                use_container_width=True,
                key=f"send_{session_id}",
            ):
                if not answer.strip():
                    st.warning("اكتب إجابتك الأول.")
                else:
                    try:
                        with st.spinner(
                            "المستثمرين بيفكروا في إجابتك..."
                        ):
                            updated = api_request(
                                "POST",
                                f"/sessions/{session_id}/turn",
                                json={"message": answer.strip()},
                                timeout=180,
                            )

                        st.session_state["session_data"] = updated
                        st.session_state.pop(
                            f"answer_{session_id}", None
                        )
                        st.rerun()

                    except requests.HTTPError as exc:
                        response = exc.response

                        if (
                            response is not None
                            and response.status_code == 409
                        ):
                            st.warning(
                                "حالة الجلسة اتغيرت. "
                                "ابدأ جلسة جديدة وجرب مرة تانية."
                            )
                        else:
                            st.error(f"فشل إرسال الإجابة: {exc}")

                    except requests.RequestException as exc:
                        st.error(f"فشل الاتصال بالـ API: {exc}")

                    except Exception as exc:
                        st.error(f"حصل خطأ: {exc}")

        else:
            st.info(
                question.get("message", "مفيش سؤال حالي.")
            )
            st.caption(
                f"المتحدث الحالي: {raw_speaker or 'غير محدد'}"
            )

    # ---------- Investor board and project summary ----------
    with right:
        st.markdown("### 🦈 مجلس المستثمرين")
        st.caption("الشخصية صاحبة الدور الحالي مميزة.")

        keys = list(AVATARS.keys())

        for row_start in range(0, len(keys), 2):
            row_keys = keys[row_start:row_start + 2]
            cols = st.columns(2)

            for col, key in zip(cols, row_keys):
                with col:
                    render_shark_card(
                        key,
                        active=(key == active_key),
                        compact=True,
                    )

        st.markdown("### 📌 ملخص المشروع")
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.write(data.get("idea", idea))
        st.markdown("</div>", unsafe_allow_html=True)

        progress = data.get("progress", {}) or {}

        st.markdown("### 📈 تقدم المقابلات")

        for key, info in progress.items():
            resolved = resolve_speaker(key) or key
            display_name = AVATARS.get(
                resolved, {}
            ).get("name", key)

            status = info.get("status", "pending")

            if status in ("complete", "completed"):
                status_label = "مكتملة"
            elif status == "in_progress":
                status_label = "جارية"
            else:
                status_label = "لم تبدأ"

            st.write(f"**{display_name}** — {status_label}")

            summary = info.get("summary", "")
            if summary:
                with st.expander(f"ملخص {display_name}"):
                    st.write(summary)

else:
    st.markdown("### 🦈 تعرّف على المستثمرين")

    cols = st.columns(4)

    for col, key in zip(cols, AVATARS):
        with col:
            render_shark_card(key, compact=True)


# ---------- Footer ----------
st.markdown(
    """
    <div style='text-align:center;color:#8f9bb0;
    padding:2rem 0 1rem;font-size:.85rem'>
        جوا التانك · دخل فكرتك وشوف هتطلع عايشة ولا لأ
    </div>
    """,
    unsafe_allow_html=True,
)
