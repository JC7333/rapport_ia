import feedparser
import os
import urllib.parse
import logging
import datetime
from deep_translator import GoogleTranslator

# ================= CONFIGURATION =================
# Vos deux chaînes YouTube avec leurs Channel IDs
YOUTUBE_CHANNELS = {
    "Shubham Sharma": "UCLKx4-_XO5sR0AO0j8ye7zQ",
    "mreflow": "UCuK2Mf5As9OKfWU7XV6yzCg"
}

# Limite de temps : vidéos publiées dans les 30 derniers jours
DAYS_LIMIT = 30

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def analyze_and_translate(text):
    try:
        traduction = GoogleTranslator(source='auto', target='fr').translate(text)
        usage = (
            "\nUsages potentiels : Cet agent IA peut automatiser des tâches, intégrer l'IA dans des applications, "
            "analyser des données et améliorer la prise de décision."
        )
        return traduction + usage
    except Exception as e:
        logging.error("Erreur lors de la traduction : " + str(e))
        return text

def generate_chatgpt_link(tool_title):
    prompt_text = (
        f"Donne-moi un guide détaillé pour installer l'outil '{tool_title}' "
        "en mettant l'accent sur la gratuité, la facilité d'installation, les prérequis et les étapes clés."
    )
    encoded_prompt = urllib.parse.quote(prompt_text)
    return f"https://chat.openai.com/?prompt={encoded_prompt}"

def generate_content():
    content = {"youtube": []}
    one_month_ago = datetime.datetime.now() - datetime.timedelta(days=DAYS_LIMIT)
    
    for channel_name, channel_id in YOUTUBE_CHANNELS.items():
        yt_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        feed = feedparser.parse(yt_url)
        if feed.entries:
            count = 0
            for entry in feed.entries:
                pub_str = entry.published.split("T")[0]
                try:
                    pub_date = datetime.datetime.strptime(pub_str, "%Y-%m-%d")
                except Exception as e:
                    logging.warning(f"Impossible de parser la date {pub_str}: {e}")
                    continue
                if pub_date < one_month_ago:
                    continue
                title = entry.title
                description = entry.get("summary", "")
                analysis = ""
                if description:
                    analysis = analyze_and_translate(description)
                content["youtube"].append({
                    "title": title,
                    "link": entry.link,
                    "published": pub_str,
                    "channel": channel_name,
                    "analysis": analysis
                })
                count += 1
                if count >= 3:
                    break
    return content

HTML_TEMPLATE = """
<html>
  <head>
    <meta charset="utf-8">
    <title>Rapport IA du {date}</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        background: #f4f4f4;
        margin: 0;
        padding: 20px;
      }}
      .container {{
        background: #ffffff;
        max-width: 800px;
        margin: auto;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }}
      h1 {{
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
      }}
      .card {{
        background: #e8f4fc;
        border-radius: 4px;
        padding: 15px;
        margin: 15px 0;
      }}
      .card h3 {{
        margin-top: 0;
      }}
      .links a {{
        margin-right: 10px;
        padding: 5px 8px;
        background: #3498db;
        color: #fff;
        text-decoration: none;
        border-radius: 3px;
        font-size: 0.9em;
      }}
      .links a:hover {{
        background: #2980b9;
      }}
      .analysis {{
        margin-top: 10px;
        font-size: 0.9em;
        color: #2c3e50;
      }}
      .footer {{
        font-size: 0.8em;
        color: #7f8c8d;
        margin-top: 20px;
        text-align: center;
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Rapport IA du {date}</h1>
      
      <h2>Vidéos Récentes</h2>
      {youtube_content}
      
      <div class="footer">
        Rapport généré à {timestamp}
      </div>
    </div>
  </body>
</html>
"""

def create_report_html(content):
    yt_html = ""
    for video in content["youtube"]:
        analysis_html = f'<p class="analysis">Résumé et usages : {video["analysis"]}</p>' if video.get("analysis") else ""
        yt_html += f"""
        <div class="card">
          <h3>{video['title']}</h3>
          <p>Chaîne : {video['channel']} | Date : {video['published']}</p>
          <div class="links">
            <a href="{video['link']}" target="_blank">Voir la vidéo</a>
            <a href="{generate_chatgpt_link(video['title'])}" target="_blank">Guide technique</a>
          </div>
          {analysis_html}
        </div>
        """
    if not yt_html:
        yt_html = "<p>Aucune vidéo pertinente ce mois-ci.</p>"
    return HTML_TEMPLATE.format(
        date=datetime.datetime.now().strftime("%d/%m/%Y"),
        youtube_content=yt_html,
        timestamp=datetime.datetime.now().strftime("%H:%M:%S")
    )

def main():
    content = generate_content()
    report_html = create_report_html(content)
    # Écrire le rapport dans le fichier index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(report_html)
    print("Rapport généré et enregistré dans index.html")

if __name__ == "__main__":
    main()
