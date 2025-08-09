import streamlit as st
import sqlite3
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv

load_dotenv()


def init_db():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT
    )
    ''')
    conn.commit()
    return conn


def get_top_article():
    try:
        response = requests.get("https://news.ycombinator.com/news")
        yc_page = response.text
        soup = BeautifulSoup(yc_page, 'html.parser')
        
        articles = soup.find_all(name='span', class_='titleline')
        article_scores = soup.find_all(name='span', class_='score')
        
        all_articles = [article.getText() for article in articles]
        all_links = [article.find('a').get("href") for article in articles]
        all_votes = [int(score.getText().split()[0]) for score in article_scores]

        highest_index = all_votes.index(max(all_votes))
        
        return all_articles[highest_index], all_links[highest_index]
    except Exception as e:
        st.error(f"Error fetching articles: {e}")
        return "Unable to fetch top article", "https://news.ycombinator.com"


def send_email(recipient, subject, message):
    try:

        sender_email = "kennedyakogokweku@gmail.com"
        password = os.getenv("password")  
        
        
        email_message = MIMEMultipart()
        email_message["From"] = sender_email
        email_message["To"] = recipient
        email_message["Subject"] = subject
        

        email_message.attach(MIMEText(message, "plain"))
        
      
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(email_message)
        
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False


def send_daily_news():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT name, email FROM subscribers")
    subscribers = c.fetchall()
    
    article_title, article_link = get_top_article()
    subject = "Top Tech News Article"
    
    success_count = 0
    total_count = len(subscribers)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (name, email) in enumerate(subscribers):
        personalized_message = f"Hi {name},\n\nToday's Top Tech article: {article_title}\nRead more at: {article_link}\n\nCheers,\n Kennedy Akogo"
        
        if send_email(email, subject, personalized_message):
            success_count += 1
        
      
        progress = (i + 1) / total_count
        progress_bar.progress(progress)
        status_text.text(f"Sending emails: {i+1}/{total_count}")
        time.sleep(0.1)  # Small delay to avoid hitting rate limits
    
    status_text.text(f"Completed! Successfully sent {success_count} out of {total_count} emails.")
    return success_count, total_count

def add_subscriber(name, email, phone):
    conn = init_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO subscribers (name, email, phone) VALUES (?, ?, ?)", 
                 (name, email, phone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        st.error("This email address is already subscribed.")
        return False
    finally:
        conn.close()


def main():
   
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    
   
    st.markdown('<div class="header-container"><h1>Tech News Service</h1></div>', unsafe_allow_html=True)
    
  
    tab1, tab2 = st.tabs(["📮 Subscribe", "🔐 Admin"])
    
   
    with tab1:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown('### 📱 Get Daily Tech News Updates')
        st.write("Subscribe to receive the top tech news article in your inbox every day. Stay informed about the latest innovations and developments in the tech world!")
        
    
        st.markdown("""
        <div style="margin-top: 15px; padding: 15px; background-color: #172554; border-radius: 8px; border: 1px solid #1E40AF;">
            <h4 style="color: #60A5FA;">How the System Works</h4>
            <p style="color: #CBD5E1; font-size: 0.9rem;">
                <strong>📰 News Source:</strong> We  get the most popular and relevant articles from <a href="https://news.ycombinator.com" style="color: #93C5FD;">Hacker News</a>, a trusted  platform for tech enthusiasts.
            </p>
            <p style="color: #CBD5E1; font-size: 0.9rem;">
                <strong>🔍 Selection Process:</strong> The system automatically selects the highest-voted article of the day, ensuring you only receive content that the tech community finds valuable and interesting.
            </p>
            <p style="color: #CBD5E1; font-size: 0.9rem;">
                <strong>⏰ Delivery:</strong> Each newsletter is delivered directly to your inbox daily, keeping you consistently updated without overwhelming you with too much content.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
  
        with st.expander("📰 See today's featured article"):
            try:
                title, link = get_top_article()
                st.markdown(f"### {title}")
                st.markdown(f"[Read the full article]({link})")
            except:
                st.write("Preview not available. Subscribe to receive articles by email!")
        
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        with st.form("subscription_form"):
            st.markdown("### Join the News-Letter ")
            name = st.text_input("Full Name", placeholder="Enter your name")
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            phone = st.text_input("Phone Number", placeholder="Optional")
            
        
            terms_agree = st.checkbox("I agree to receive daily tech news updates")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("🚀 Subscribe Now")
            
            if submitted:
                if not name or not email:
                    st.error("Please fill in all required fields.")
                elif "@" not in email:
                    st.error("Please enter a valid email address.")
                elif not terms_agree:
                    st.error("Please agree to receive the newsletter to subscribe.")
                else:
                    if add_subscriber(name, email, phone):
                        st.markdown('<div class="success-message">', unsafe_allow_html=True)
                        st.success("🎉 You have successfully subscribed!")
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.balloons()
                        
                        st.markdown("""
                        <div style="background-color: #172554; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px; border: 1px solid #1E40AF;">
                            <h3 style="color: white;">Welcome to our Tech Community!</h3>
                            <p style="color: #CBD5E1;">Your first newsletter will arrive shortly. Meanwhile, check out our featured article for today!</p>
                            <p style="font-size: 0.8rem; color: #94A3B8;">You can unsubscribe at any time by clicking the link in the email.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                 
                        welcome_subject = "Welcome to My Tech News Subscription!"
                        welcome_message = f"""Hi {name},

Thank you for subscribing to my Tech News service! 🎉

You'll now receive daily updates on the lastest tech trends directly in your inbox. I have curated the most interesting and impactful stories from around the tech world to keep you informed.

Today's Top Article:
{get_top_article()[0]}

I am excited to have you join my tech community!
As a promise to you, I will constantly work to improve this service and provide even more value to subscribers like you.

Cheers,
Kennedy - AI/LLM engineer.
"""
                        send_email(email, welcome_subject, welcome_message)
        
        st.markdown('</div>', unsafe_allow_html=True)
        

    with tab2:
        st.markdown('<div class="tech-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Admin Dashboard")
        st.markdown("Access the administrative functions to manage subscribers and send newsletters.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if not st.session_state.is_admin:
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            with st.form("admin_login"):
                st.markdown("### Admin Login")
                password = st.text_input("Admin Password", type="password", placeholder="Enter admin password")
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    login_submitted = st.form_submit_button("🔑 Login")
                
                if login_submitted:
                  
                    if password == os.getenv("ADMIN_PASSWORD"):
                        st.session_state.is_admin = True
                        st.rerun()
                    else:
                        st.error("Incorrect password")
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.success("✅ Admin logged in successfully")
            
         
            conn = init_db()
            df = pd.read_sql_query("SELECT * FROM subscribers", conn)
            conn.close()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                subscriber_count = len(df)
                st.markdown(f"""
                <div style="background-color: #172554; padding: 20px; border-radius: 10px; text-align: center; height: 150px; border: 1px solid #1E40AF;">
                    <h4 style="color: #60A5FA;">Total Subscribers</h4>
                    <h2 style="font-size: 3rem; margin: 10px 10px; color: white;">{subscriber_count}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                today = pd.Timestamp.now().strftime('%Y-%m-%d')
               
                new_today = len(df[df['id'] == df['id'].max()]) if not df.empty else 0
                st.markdown(f"""
                <div style="background-color: #172554; padding: 20px; border-radius: 10px; text-align: center; height: 150px; border: 1px solid #1E40AF;">
                    <h4 style="color: #60A5FA;">New Today</h4>
                    <h2 style="font-size: 3rem; margin: 10px 0; color: white;">{new_today}</h2>
                </div>
                """, unsafe_allow_html=True)
  
      
            
            with col3:
                st.markdown("""
                <div style="background-color: #172554; padding: 20px; border-radius: 10px; text-align: center; height: 150px; border: 1px solid #1E40AF;">
                    <h4 style="color: #60A5FA;">Newsletter Status</h4>
                    <h2 style="font-size: 1.5rem; margin: 10px 0; color: #FBBF24;">Ready to Send</h2>
                </div>
                """, unsafe_allow_html=True)
            
           
            st.markdown("""
            <div style="background-color: #1E3A8A; padding: 25px; border-radius: 10px; margin: 20px 0; border: 1px solid #2563EB;">
                <h3 style="color: white; text-align: center;">Newsletter Control Panel</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
              
                st.markdown('<div style="background-color: #172554; padding: 20px; border-radius: 10px; height: 100%; border: 1px solid #1E40AF;">', unsafe_allow_html=True)
                st.markdown("### 📰 Today's Newsletter")
                try:
                    title, link = get_top_article()
                    st.markdown(f"**Title:** {title}")
                    st.markdown(f"**Link:** [Read the full article]({link})")
                    st.markdown("**Preview:**")
                    st.info(f"Today's Top Tech article: {title}\nRead more at: {link}")
                except:
                    st.error("Unable to fetch today's article. Please try again later.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
              
                st.markdown('<div style="background-color: #172554; padding: 20px; border-radius: 10px; height: 100%; border: 1px solid #1E40AF;">', unsafe_allow_html=True)
                st.markdown("### 📤 Send Newsletter")
                st.write("Send the daily newsletter to all subscribers with one click.")
                
                if st.button("📧 Send to All Subscribers", use_container_width=True):
                    with st.spinner("Preparing to send newsletters..."):
                       
                        progress_container = st.empty()
                        progress_container.markdown("""
                        <div style="background-color: #075985; padding: 20px; border-radius: 10px; text-align: center;">
                            <h4 style="color: white;">Preparing newsletter...</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        success_count, total_count = send_daily_news()
                        
                    if success_count > 0:
                        progress_container.markdown(f"""
                        <div style="background-color: #065F46; padding: 20px; border-radius: 10px; text-align: center;">
                            <h4 style="color: white;">✅ Successfully sent {success_count} out of {total_count} emails!</h4>
                            <p style="color: #A7F3D0;">The newsletter has been delivered to your subscribers.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        progress_container.markdown("""
                        <div style="background-color: #7F1D1D; padding: 20px; border-radius: 10px; text-align: center;">
                            <h4 style="color: white;">❌ Failed to send emails</h4>
                            <p style="color: #FECACA;">Please check your email configuration and try again.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
             
                st.markdown("### 🧪 Test Newsletter")
                test_email = st.text_input("Send test to email", placeholder="your.email@example.com")
                if st.button("📤 Send Test Email", use_container_width=True) and test_email:
                    if "@" in test_email:
                        with st.spinner("Sending test email..."):
                            title, link = get_top_article()
                            subject = "Tech News Newsletter - TEST"
                            message = f"""Hi there,

This is a TEST email of our Tech News newsletter.

Today's Top Tech article: {title}
Read more at: {link}

Thanks for being a subscriber!
Tech News Team
"""
                            if send_email(test_email, subject, message):
                                st.success("✅ Test email sent successfully!")
                            else:
                                st.error("❌ Failed to send test email.")
                    else:
                        st.error("Please enter a valid email address for testing.")
                st.markdown('</div>', unsafe_allow_html=True)
            
           
            st.markdown("""
            <div style="background-color: #1E3A8A; padding: 25px; border-radius: 10px; margin: 20px 0; border: 1px solid #2563EB;">
                <h3 style="color: white; text-align: center;">Subscriber Management</h3>
            </div>
            """, unsafe_allow_html=True)
            

            st.markdown("### 👥 Current Subscribers")
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    # Export options
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Export as CSV",
                        data=csv,
                        file_name="subscribers.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                  
                    if st.button("🚪 Logout", use_container_width=True):
                        st.session_state.is_admin = False
                        st.rerun()
            else:
                st.info("No subscribers yet. Share your subscription form to get started!")
                
                
                if st.button("🚪 Logout", use_container_width=True):
                    st.session_state.is_admin = False
                    st.rerun()

# 

def add_floating_icons():
    icons = "🔧 💻 📱 🌐 🔍 📊 🚀 🔒 🌟 📡"
    html = '<div class="floating-icons">'
    
    for i in range(15):
        icon = icons[i % len(icons)]
        left = i * 7
        delay = i * 0.5
        top = (i * 13) % 90
        html += f'<div class="tech-float" style="left:{left}%; top:{top}%; animation-delay:{delay}s;">{icon}</div>'
    
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

add_floating_icons()

if __name__ == "__main__":
    main()