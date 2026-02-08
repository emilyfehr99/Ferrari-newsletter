"""
Ferrari F1 Newsletter - Template Renderer Module
Renders the HTML email template with scraped content
"""

import os
import requests
from datetime import datetime
from typing import List, Optional
from news_scraper import Article
import logging

logger = logging.getLogger(__name__)


class TemplateRenderer:
    """Renders the newsletter HTML template with article content"""
    
    # Category colors for styling
    CATEGORY_COLORS = {
        "Race Weekend": "#EF1A2D",
        "Technical": "#000000",
        "Driver News": "#00A551",
        "Strategy": "#FFF200",
        "General": "#888888",
        "Official": "#EF1A2D"
    }
    
    # Category icons
    CATEGORY_ICONS = {
        "Race Weekend": "🏁",
        "Technical": "⚙️",
        "Driver News": "👤",
        "Strategy": "📊",
        "General": "📰",
        "Official": "🏎️"
    }
    
    def __init__(self, template_dir: str = None):
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.template_dir = template_dir
    
    def render(self, selected_articles: dict, 
               driver_standings: dict = None,
               constructor_standings: dict = None,
               is_email: bool = False) -> str:
        """Render the complete newsletter HTML"""
        
        # Default standings if not provided
        if driver_standings is None:
            driver_standings = self._get_default_driver_standings()
        if constructor_standings is None:
            constructor_standings = self._get_default_constructor_standings()
        
        # Build article sections
        featured_html = self._render_featured_article(selected_articles.get("featured", []))
        headlines_html = self._render_headlines(selected_articles.get("headlines", []))
        technical_html = self._render_technical(selected_articles.get("technical", []))
        
        # Get current date
        newsletter_date = datetime.now().strftime("%B %d, %Y")
        
        # Build the complete HTML
        html = self._build_complete_html(
            newsletter_date=newsletter_date,
            featured_html=featured_html,
            headlines_html=headlines_html,
            technical_html=technical_html,
            driver_standings=driver_standings,
            constructor_standings=constructor_standings,
            is_email=is_email
        )
        
        return html
    
    def _render_featured_article(self, articles: List[Article]) -> str:
        """Render the featured article section"""
        if not articles:
            return ""
        
        article = articles[0]
        category_color = self.CATEGORY_COLORS.get(article.category, "#EF1A2D")
        category_icon = self.CATEGORY_ICONS.get(article.category, "📰")
        
        return f'''
        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
            <tr>
                <td class="mobile-padding" style="padding: 0 50px 20px 50px;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%); border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.15);">
                        <tr>
                            <td style="padding: 28px 30px;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                    <tr>
                                        <td style="background: linear-gradient(90deg, {category_color}, {category_color}dd); border-radius: 20px; padding: 5px 14px;">
                                            <span style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 9px; font-weight: 700; color: #FFFFFF; letter-spacing: 1.5px; text-transform: uppercase;">{category_icon} {article.category.upper()}</span>
                                        </td>
                                    </tr>
                                </table>
                                <h3 style="margin: 16px 0 10px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 20px; font-weight: 700; color: #FFFFFF; line-height: 1.35;">
                                    {article.title}
                                </h3>
                                <p style="margin: 0 0 14px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; color: #888888; font-weight: 500;">
                                    {article.source.upper()} · {article.published_date.strftime("%b %d, %Y").upper()}
                                </p>
                                <p style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 13.5px; line-height: 1.7; color: #CCCCCC;">
                                    {article.summary}
                                </p>
                                <p style="margin: 18px 0 0 0;"><a href="{article.url}" target="_blank" style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 12px; font-weight: 700; color: #FFF200; text-decoration: none; letter-spacing: 1px;">READ FULL ARTICLE →</a></p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        '''
    
    def _render_headlines(self, articles: List[Article]) -> str:
        """Render the headlines section"""
        if not articles:
            return ""
        
        html_parts = []
        for article in articles:
            category_color = self.CATEGORY_COLORS.get(article.category, "#888888")
            category_icon = self.CATEGORY_ICONS.get(article.category, "📰")
            
            html_parts.append(f'''
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                <tr>
                    <td class="mobile-padding" style="padding: 0 50px 15px 50px;">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: #FFFFFF; border: 1px solid #E8E8E8; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                            <tr>
                                <td style="padding: 22px 26px;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td width="5" style="background: linear-gradient(180deg, {category_color}, {category_color}aa); border-radius: 3px;"></td>
                                            <td style="padding-left: 18px;">
                                                <p style="margin: 0 0 6px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 9px; font-weight: 700; color: {category_color}; letter-spacing: 1.5px; text-transform: uppercase;">{category_icon} {article.category.upper()}</p>
                                                <h3 style="margin: 0 0 8px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 16px; font-weight: 700; color: #1a1a1a; line-height: 1.35;">
                                                    {article.title}
                                                </h3>
                                                <p style="margin: 0 0 10px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 10px; color: #999999; font-weight: 500;">
                                                    {article.source.upper()} · {article.published_date.strftime("%b %d, %Y").upper()}
                                                </p>
                                                <p style="margin: 0 0 12px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 13px; line-height: 1.6; color: #555555;">
                                                    {article.summary}
                                                </p>
                                                <a href="{article.url}" target="_blank" style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; font-weight: 700; color: #EF1A2D; text-decoration: none;">Read full article →</a>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            ''')
        
        return '\n'.join(html_parts)
    
    def _render_technical(self, articles: List[Article]) -> str:
        """Render the technical corner section"""
        if not articles:
            return ""
        
        tech_icons = ["🌬️", "⚡", "🔧", "🏎️", "📈"]
        html_parts = []
        
        for i, article in enumerate(articles):
            icon = tech_icons[i % len(tech_icons)]
            
            html_parts.append(f'''
            <tr>
                <td style="padding: 18px 30px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                            <td width="45" style="vertical-align: top;">
                                <div style="background: linear-gradient(135deg, #EF1A2D, #FF4D5A); border-radius: 10px; width: 42px; height: 42px; text-align: center; line-height: 42px;">
                                    <span style="font-size: 20px;">{icon}</span>
                                </div>
                            </td>
                            <td style="padding-left: 16px; vertical-align: top;">
                                <h4 style="margin: 0 0 6px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 14px; font-weight: 700; color: #FFFFFF;">
                                    {article.title}
                                </h4>
                                <p style="margin: 0 0 4px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 10px; color: #666666; font-weight: 500;">
                                    {article.source.upper()} · {article.published_date.strftime("%b %d").upper()}
                                </p>
                                <p style="margin: 0 0 8px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 13px; line-height: 1.5; color: #999999;">
                                    {article.summary}
                                </p>
                                <a href="{article.url}" target="_blank" style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 10px; font-weight: 700; color: #FFF200; text-decoration: none;">Read more →</a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            ''')
        
        return '\n'.join(html_parts)
    
    def _get_default_driver_standings(self) -> dict:
        """Fetch Ferrari driver standings from Ergast API"""
        return self._fetch_ferrari_standings()["drivers"]
    
    def _get_default_constructor_standings(self) -> dict:
        """Fetch Ferrari constructor standings from Ergast API"""
        return self._fetch_ferrari_standings()["constructor"]
    
    def _fetch_ferrari_standings(self) -> dict:
        """Fetch live standings from Ergast F1 API"""
        try:
            # Get driver standings
            driver_resp = requests.get(
                "https://api.jolpi.ca/ergast/f1/current/driverStandings.json",
                timeout=10
            )
            driver_resp.raise_for_status()
            driver_data = driver_resp.json()
            
            # Get constructor standings
            const_resp = requests.get(
                "https://api.jolpi.ca/ergast/f1/current/constructorStandings.json",
                timeout=10
            )
            const_resp.raise_for_status()
            const_data = const_resp.json()
            
            # Find Ferrari drivers
            standings = driver_data["MRData"]["StandingsTable"]["StandingsLists"]
            ferrari_drivers = []
            
            if standings:
                for driver in standings[0]["DriverStandings"]:
                    if "ferrari" in driver["Constructors"][0]["constructorId"].lower():
                        ferrari_drivers.append({
                            "name": driver["Driver"]["familyName"].upper(),
                            "points": int(float(driver["points"])),
                            "position": int(driver["position"])
                        })
            
            # Find Ferrari in constructors
            const_standings = const_data["MRData"]["StandingsTable"]["StandingsLists"]
            ferrari_const = {"points": 0, "position": 0}
            
            if const_standings:
                for team in const_standings[0]["ConstructorStandings"]:
                    if "ferrari" in team["Constructor"]["constructorId"].lower():
                        ferrari_const = {
                            "points": int(float(team["points"])),
                            "position": int(team["position"])
                        }
                        break
            
            # Return Ferrari data (or defaults)
            if len(ferrari_drivers) >= 2:
                return {
                    "drivers": {
                        "driver1": ferrari_drivers[0],
                        "driver2": ferrari_drivers[1]
                    },
                    "constructor": ferrari_const
                }
            
        except Exception as e:
            logger.warning(f"Failed to fetch Ergast API standings: {e}")
        
        # Dynamic Pre-Season Placeholder
        bahrain_gp = datetime(2026, 3, 1) # Estimated date
        days_to_bahrain = (bahrain_gp - datetime.now()).days
        status_msg = f"{max(0, days_to_bahrain)} DAYS UNTIL BAHRAIN" if days_to_bahrain > 0 else "PRE-SEASON"

        return {
            "drivers": {
                "driver1": {"name": "LECLERC", "points": status_msg, "position": "-"},
                "driver2": {"name": "HAMILTON", "points": status_msg, "position": "-"}
            },
            "constructor": {"points": status_msg, "position": "-"}
        }
    
    def _build_complete_html(self, newsletter_date: str, featured_html: str,
                             headlines_html: str, technical_html: str,
                             driver_standings: dict, constructor_standings: dict,
                             is_email: bool = False) -> str:
        """Build the complete newsletter HTML"""
        
        d1 = driver_standings["driver1"]
        d2 = driver_standings["driver2"]
        cs = constructor_standings
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ferrari F1 Weekly Digest</title>
    <link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 50%, #0d0d0d 100%); font-family: 'Titillium Web', Arial, sans-serif; }}
        table {{ border-spacing: 0; border-collapse: collapse; }}
        @media screen and (max-width: 680px) {{
            .email-container {{ width: 100% !important; }}
            .stack-column {{ display: block !important; width: 100% !important; margin-bottom: 15px !important; }}
            .mobile-padding {{ padding-left: 20px !important; padding-right: 20px !important; }}
            .driver-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(239,26,45,0.4) !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 50%, #0d0d0d 100%);">
    
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 50%, #0d0d0d 100%);">
        <tr>
            <td align="center" style="padding: 40px 15px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="680" class="email-container" style="background: linear-gradient(180deg, #141414 0%, #1a1a1a 100%); border-radius: 20px; overflow: hidden; box-shadow: 0 25px 80px rgba(239, 26, 45, 0.15);">
                    
                    <!-- HEADER -->
                    <tr>
                        <td>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="33.33%" style="background: linear-gradient(90deg, #00A551 0%, #00B85A 100%); height: 4px;"></td>
                                    <td width="33.33%" style="background: #FFFFFF; height: 4px;"></td>
                                    <td width="33.34%" style="background: linear-gradient(90deg, #EF1A2D 0%, #FF2D40 100%); height: 4px;"></td>
                                </tr>
                            </table>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="background: linear-gradient(145deg, #C41422 0%, #EF1A2D 30%, #FF3344 70%, #EF1A2D 100%); padding: 40px 40px 30px 40px; text-align: center;">
                                        <img src="{'cid:ferrari_logo' if is_email else 'assets/ferrari_logo.png'}" alt="Scuderia Ferrari" width="60" style="display: block; margin: 0 auto 15px auto; width: 60px; max-width: 60px;">
                                        <h1 style="margin: 0 0 8px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 32px; font-weight: 900; color: #FFF200; letter-spacing: 6px; text-transform: uppercase; text-shadow: 0 2px 20px rgba(255,242,0,0.4);">
                                            MARANELLO INSIDER
                                        </h1>
                                        <p style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.85); letter-spacing: 5px; text-transform: uppercase;">
                                            EXCLUSIVE TECHNICAL ANALYSIS & INSIDER NEWS
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="background: rgba(0,0,0,0.25); padding: 14px 40px; text-align: center;">
                                        <p style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; font-weight: 600; color: #FFF200; letter-spacing: 3px;">
                                            ◆ WEEK OF {newsletter_date.upper()} ◆
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- CONTENT -->
                    <tr>
                        <td style="background: linear-gradient(180deg, #FFFFFF 0%, #F5F5F5 100%); padding: 45px 0 0 0;">
                            
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td class="mobile-padding" style="padding: 0 50px 35px 50px;">
                                        <p style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 17px; line-height: 1.7; color: #333333;">
                                            <span style="color: #EF1A2D; font-weight: 700; font-size: 19px;">Ciao Tifosi!</span> Here's your weekly roundup of Ferrari F1 news, technical developments, and race analysis from Maranello.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td class="mobile-padding" style="padding: 0 50px 20px 50px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td style="border-left: 3px solid #EF1A2D; padding-left: 18px;">
                                                    <p style="margin: 0 0 3px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 10px; font-weight: 600; color: #EF1A2D; letter-spacing: 2px;">THIS WEEK</p>
                                                    <h2 style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 22px; font-weight: 700; color: #000000;">Top Headlines</h2>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            {featured_html}
                            {headlines_html}
                            
                            <!-- TECHNICAL CORNER -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td class="mobile-padding" style="padding: 25px 50px 20px 50px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%); border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
                                            <tr>
                                                <td style="padding: 25px 30px 20px 30px; border-bottom: 1px solid rgba(255,242,0,0.15);">
                                                    <p style="margin: 0 0 5px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 9px; font-weight: 700; color: #FFF200; letter-spacing: 2px;">ENGINEERING UPDATES</p>
                                                    <h2 style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 20px; font-weight: 700; color: #FFFFFF;">⚙️ Technical Corner</h2>
                                                </td>
                                            </tr>
                                            {technical_html}
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- DRIVER STANDINGS -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td class="mobile-padding" style="padding: 25px 50px 15px 50px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                            <tr>
                                                <td style="border-left: 3px solid #FFF200; padding-left: 18px;">
                                                    <p style="margin: 0 0 3px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 10px; font-weight: 600; color: #888888; letter-spacing: 2px;">CHAMPIONSHIP</p>
                                                    <h2 style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 22px; font-weight: 700; color: #000000;">🏆 Driver Standings</h2>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td class="mobile-padding" style="padding: 10px 50px 25px 50px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td width="48%" class="stack-column" style="vertical-align: top;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(145deg, #C41422 0%, #EF1A2D 50%, #FF3344 100%); border-radius: 16px; box-shadow: 0 10px 30px rgba(239,26,45,0.3);">
                                                        <tr>
                                                            <td style="padding: 25px; text-align: center;">
                                                                 <p style="margin: 0 0 4px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 9px; color: rgba(255,255,255,0.7); letter-spacing: 3px; font-weight: 600;">DRIVER</p>
                                                                <h3 style="margin: 0 0 15px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 26px; font-weight: 900; color: #FFFFFF; letter-spacing: 2px;">{d1["name"]}</h3>
                                                                <div style="display: inline-block; background: linear-gradient(135deg, #FFF200 0%, #FFE600 100%); border-radius: 30px; padding: 10px 28px; box-shadow: 0 4px 20px rgba(255,242,0,0.4);">
                                                                    <span style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 28px; font-weight: 900; color: #000000;">{d1["points"]}</span>
                                                                    <span style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; color: #333333; font-weight: 700; margin-left: 4px;">PTS</span>
                                                                </div>
                                                                <p style="margin: 15px 0 0 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 12px; color: rgba(255,255,255,0.85);">
                                                                    Position: <strong style="color: #FFF200; font-size: 14px;">P{d1["position"]}</strong>
                                                                </p>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                                <td width="4%"></td>
                                                <td width="48%" class="stack-column" style="vertical-align: top;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(145deg, #C41422 0%, #EF1A2D 50%, #FF3344 100%); border-radius: 16px; box-shadow: 0 10px 30px rgba(239,26,45,0.3);">
                                                        <tr>
                                                            <td style="padding: 25px; text-align: center;">
                                                                <p style="margin: 0 0 4px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 9px; color: rgba(255,255,255,0.7); letter-spacing: 3px; font-weight: 600;">DRIVER</p>
                                                                <h3 style="margin: 0 0 15px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 26px; font-weight: 900; color: #FFFFFF; letter-spacing: 2px;">{d2["name"]}</h3>
                                                                <div style="display: inline-block; background: linear-gradient(135deg, #FFF200 0%, #FFE600 100%); border-radius: 30px; padding: 10px 28px; box-shadow: 0 4px 20px rgba(255,242,0,0.4);">
                                                                    <span style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 28px; font-weight: 900; color: #000000;">{d2["points"]}</span>
                                                                    <span style="font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; color: #333333; font-weight: 700; margin-left: 4px;">PTS</span>
                                                                </div>
                                                                <p style="margin: 15px 0 0 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 12px; color: rgba(255,255,255,0.85);">
                                                                    Position: <strong style="color: #FFF200; font-size: 14px;">P{d2["position"]}</strong>
                                                                </p>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CONSTRUCTORS -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td class="mobile-padding" style="padding: 10px 50px 40px 50px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%); border-radius: 14px; border: 1px solid rgba(255,242,0,0.1);">
                                            <tr>
                                                <td style="padding: 22px 28px;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                                        <tr>
                                                            <td>
                                                                <p style="margin: 0 0 4px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 9px; color: #666666; letter-spacing: 2px; font-weight: 600;">CONSTRUCTORS CHAMPIONSHIP</p>
                                                                <h3 style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 18px; font-weight: 700; color: #EF1A2D; letter-spacing: 1px;">SCUDERIA FERRARI</h3>
                                                            </td>
                                                            <td style="text-align: right;">
                                                                <p style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 36px; font-weight: 900; color: #FFF200; text-shadow: 0 0 20px rgba(255,242,0,0.3);">{cs["points"]}</p>
                                                                <p style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; color: #666666; letter-spacing: 1px; font-weight: 600;">POINTS • P{cs["position"]}</p>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                        </td>
                    </tr>
                    
                    <!-- SIGNUP CTA -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%); padding: 40px 50px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #EF1A2D; background: linear-gradient(135deg, #EF1A2D 0%, #C41422 100%); border-radius: 16px; overflow: hidden;">
                                <tr>
                                    <td style="padding: 35px 40px; text-align: center;">
                                        <h3 style="margin: 0 0 12px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 22px; font-weight: 900; color: #FFFFFF; letter-spacing: 1px;">📧 SUBSCRIBE FOR WEEKLY UPDATES</h3>
                                        <p style="margin: 0 0 25px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 14px; color: rgba(255,255,255,0.85);">Get the latest Ferrari F1 news, technical analysis, and race insights delivered every Sunday.</p>
                                        <a href="https://ferrari-newsletter.vercel.app/signup.html" style="display: inline-block; padding: 16px 40px; background-color: #FFF200; background: linear-gradient(135deg, #FFF200 0%, #FFE600 100%); border-radius: 10px; text-decoration: none; font-family: 'Titillium Web', Arial, sans-serif; font-size: 14px; font-weight: 900; color: #000000; letter-spacing: 1.5px; text-transform: uppercase; box-shadow: 0 6px 25px rgba(255,242,0,0.3);">🏎️ SUBSCRIBE NOW</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- FOOTER -->
                    <tr>
                        <td style="background: linear-gradient(180deg, #0d0d0d 0%, #000000 100%); padding: 45px 50px; text-align: center;">
                            <h3 style="margin: 0 0 12px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 22px; font-weight: 900; color: #FFFFFF; letter-spacing: 2px;">FORZA FERRARI! 🇮🇹</h3>
                            <p style="margin: 0 0 25px 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 14px; color: #777777;">Stay passionate, stay informed. See you at the next race!</p>
                            <p style="margin: 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px; color: #555555;">Curated with ❤️ for Ferrari fans worldwide</p>
                            <p style="margin: 15px 0 0 0; font-family: 'Titillium Web', Arial, sans-serif; font-size: 11px;"><a href="https://ferrari-newsletter.vercel.app/unsubscribe.html" style="color: #888888; text-decoration: underline;">Unsubscribe</a> · <a href="https://ferrari-newsletter.vercel.app/privacy.html" style="color: #888888; text-decoration: underline;">Privacy Policy</a> · <a href="https://ferrari-newsletter.vercel.app/" style="color: #888888; text-decoration: underline;">View in Browser</a></p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td width="33.33%" style="background: linear-gradient(90deg, #00A551 0%, #00B85A 100%); height: 4px;"></td>
                                    <td width="33.33%" style="background: #FFFFFF; height: 4px;"></td>
                                    <td width="33.34%" style="background: linear-gradient(90deg, #EF1A2D 0%, #FF2D40 100%); height: 4px;"></td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
    
</body>
</html>'''


if __name__ == "__main__":
    # Test with sample data
    from news_scraper import Article
    from datetime import datetime
    
    sample_articles = {
        "featured": [
            Article(
                title="Ferrari Unveils Revolutionary Front Wing for Australian GP",
                summary="Scuderia Ferrari has revealed an aggressive upgrade package featuring a revolutionary front wing design aimed at improving cornering performance and reducing understeer in slow-speed corners. The new design incorporates advanced aerodynamic concepts developed through extensive CFD simulations and wind tunnel testing at Maranello.",
                source="Motorsport.com",
                url="",
                published_date=datetime.now(),
                category="Technical"
            )
        ],
        "headlines": [
            Article(
                title="Leclerc: 2026 Car Feels Like a Major Step Forward",
                summary="Charles Leclerc expressed optimism after completing his first extended run in the SF-26, highlighting improvements in the car's balance and overall driveability compared to last year's challenger.",
                source="F1.com",
                url="",
                published_date=datetime.now(),
                category="Driver News"
            )
        ],
        "technical": [
            Article(
                title="New Sidepod Undercut Design Analysis",
                summary="Ferrari's revised sidepod features a more aggressive undercut, improving airflow to the rear of the car. Estimated 3-4% improvement in diffuser downforce.",
                source="The Race",
                url="",
                published_date=datetime.now(),
                category="Technical"
            )
        ]
    }
    
    renderer = TemplateRenderer()
    html = renderer.render(sample_articles)
    
    # Save to file for preview
    with open("../index.html", "w") as f:
        f.write(html)
    
    print("Generated newsletter saved to index.html")


if __name__ == "__main__":
    # Test with sample data
    from news_scraper import Article
    from datetime import datetime
    
    sample_articles = {
        "featured": [
            Article(
                title="Ferrari Unveils Revolutionary Front Wing for Australian GP",
                summary="Scuderia Ferrari has revealed an aggressive upgrade package featuring a revolutionary front wing design aimed at improving cornering performance and reducing understeer in slow-speed corners. The new design incorporates advanced aerodynamic concepts developed through extensive CFD simulations and wind tunnel testing at Maranello.",
                source="Motorsport.com",
                url="",
                published_date=datetime.now(),
                category="Technical"
            )
        ],
        "headlines": [
            Article(
                title="Leclerc: 2026 Car Feels Like a Major Step Forward",
                summary="Charles Leclerc expressed optimism after completing his first extended run in the SF-26, highlighting improvements in the car's balance and overall driveability compared to last year's challenger.",
                source="F1.com",
                url="",
                published_date=datetime.now(),
                category="Driver News"
            )
        ],
        "technical": [
            Article(
                title="New Sidepod Undercut Design Analysis",
                summary="Ferrari's revised sidepod features a more aggressive undercut, improving airflow to the rear of the car. Estimated 3-4% improvement in diffuser downforce.",
                source="The Race",
                url="",
                published_date=datetime.now(),
                category="Technical"
            )
        ]
    }
    
    renderer = TemplateRenderer()
    html = renderer.render(sample_articles)
    
    # Save to file for preview
    with open("../templates/generated_preview.html", "w") as f:
        f.write(html)
    
    print("Generated newsletter saved to templates/generated_preview.html")
