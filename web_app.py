import sqlite3
import streamlit as st

st.set_page_config(
    page_title="СУБД ПК Комплектуючі", page_icon="🖥️", layout="centered"
)


def get_connection():
    return sqlite3.connect("pc_hardware.db")


st.title("🖥️ Підбір ПК та База Комплектуючих")
st.write("Ласкаво просимо до системи управління та автоматичного підбору ПК!")

menu = st.sidebar.radio(
    "Навігація",
    [
        "📋 Всі деталі",
        "➕ Додати деталь",
        "🖥️ Підбір за бюджетом",
        "📊 Статистика",
    ],
)

conn = get_connection()

if menu == "📋 Всі деталі":
    st.header("📋 Список комплектуючих на складі")
    cursor = conn.cursor()
    query = """
    SELECT components.name AS "Назва деталі", components.price AS "Ціна (грн)", categories.name AS "Категорія"
    FROM components 
    JOIN categories ON components.category_id = categories.id;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if rows:
        st.dataframe(
            rows,
            column_config={
                "0": "Назва деталі",
                "1": "Ціна (грн)",
                "2": "Категорія",
            },
            use_container_width=True,
        )
    else:
        st.info("База даних порожня.")

elif menu == "➕ Додати деталь":
    st.header("➕ Додати нову деталь")
    with st.form("add_form"):
        name = st.text_input("Назва деталі")
        price = st.number_input("Ціна (грн)", min_value=1, value=1000, step=100)
        category_id = st.selectbox(
            "Категорія",
            options=[1, 2, 3],
            format_func=lambda x: {
                1: "Процесори",
                2: "Відеокарти",
                3: "SSD",
            }[x],
        )
        submitted = st.form_submit_button("Зберегти деталь")

        if submitted:
            if not name.strip():
                st.error("Назва не може бути порожньою!")
            else:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO components (name, price, category_id) VALUES (?, ?, ?)",
                    (name.strip(), price, category_id),
                )
                conn.commit()
                st.success(f"✅ Успішно додано: {name} за {price} грн!")

elif menu == "🖥️ Підбір за бюджетом":
    st.header("🎯 Автоматичний підбір збірки ПК")
    budget = st.number_input(
        "Введіть ваш бюджет (грн)", min_value=1000, value=25000, step=500
    )

    if st.button("Зібрати ПК"):
        cursor = conn.cursor()
        query = """
        SELECT 
            cpu.name, cpu.price,
            gpu.name, gpu.price,
            ssd.name, ssd.price,
            (cpu.price + gpu.price + ssd.price) AS total_price
        FROM 
            (SELECT name, price FROM components WHERE category_id = 1) cpu,
            (SELECT name, price FROM components WHERE category_id = 2) gpu,
            (SELECT name, price FROM components WHERE category_id = 3) ssd
        WHERE 
            (cpu.price + gpu.price + ssd.price) <= ?
        ORDER BY 
            total_price DESC
        LIMIT 1;
        """
        cursor.execute(query, (budget,))
        build = cursor.fetchone()

        if build:
            (
                cpu_name,
                cpu_price,
                gpu_name,
                gpu_price,
                ssd_name,
                ssd_price,
                total,
            ) = build
            st.success(f"Збірку знайдено! Загальна сума: {total} грн")

            col1, col2, col3 = st.columns(3)
            col1.metric("Процесор", cpu_name, f"{cpu_price} грн")
            col2.metric("Відеокарта", gpu_name, f"{gpu_price} грн")
            col3.metric("Накопичувач", ssd_name, f"{ssd_price} грн")

            st.info(f"💵 Залишок від бюджету: {budget - total} грн")
        else:
            st.warning(
                f"На бюджет {budget} грн не вдалося зібрати ПК. У базі немає достатньо дешевих комплектуючих."
            )

elif menu == "📊 Статистика":
    st.header("📊 Статистика бази даних")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*), COALESCE(SUM(price), 0), COALESCE(AVG(price), 0) FROM components;"
    )
    total_count, total_sum, avg_price = cursor.fetchone()

    if total_count > 0:
        cursor.execute("SELECT name, MAX(price) FROM components;")
        max_item, max_price = cursor.fetchone()

        col1, col2 = st.columns(2)
        col1.metric("Всього позицій", total_count)
        col2.metric("Загальна вартість склада", f"{total_sum} грн")

        col3, col4 = st.columns(2)
        col3.metric("Середня ціна", f"{round(avg_price, 2)} грн")
        col4.metric("Найдорожчий товар", max_item, f"{max_price} грн")
    else:
        st.info("База даних порожня.")

conn.close()