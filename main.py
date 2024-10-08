import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import cv2
import numpy as np

# URL of the published Google Sheet
SHEET_URL = st.secrets['google_sheet_url']

# Banner sizes for different platforms
BANNER_SIZES = {
    "Twitter": (1500, 500),
    "LinkedIn": (1584, 396),
    "Substack": (1110, 220)
}

# Function to fetch the usernames from the sheet
def fetch_usernames():
    df = pd.read_csv(SHEET_URL)
    return df['custom_redirect'].dropna().unique()

# Fetch user data from Google Sheets
def get_user_data(username):
    # Read the published Google Sheet
    df = pd.read_csv(SHEET_URL)
    
    # Find all rows with the matching username in the 'custom_redirect' column
    user_rows = df[df['custom_redirect'].str.lower() == username.lower()]
    
    # Convert 'Rank' column to datetime
    user_rows['Rank'] = pd.to_datetime(user_rows['Rank'], format='%b %d, %Y', errors='coerce')

    if user_rows.empty:
        return None
    
    # Sort the rows by 'Rank' column in descending order and select the top 3 rows
    latest_rows = user_rows.sort_values('Rank', ascending=False).head(3)
    
    # Get the logo URLs from the 'logoUrl' column
    logos = []
    
    for url in latest_rows['logoUrl']:
        # Append token if it's a 'logo.dev' URL
        if "logo.dev" in url:
            url += f"?token={st.secrets['logo_dev_api_key']}"
            logos.append(url)
        else:
            logos.append(url)
    
    
    # Get the stock titles from the 'title' column
    stock_titles = latest_rows['title'].tolist()

    # Remove any invalid URLs
    logos = [logo for logo in logos if pd.notna(logo) and logo.startswith('https')]
    
    return {
        'logos': logos,
        'stock_titles': stock_titles, 
        'username': username
    }

# Fetch template image from a URL
def get_template_image(template_url):
    response = requests.get(template_url)
    template = Image.open(BytesIO(response.content))
    return template

# Create banner image with logos and stock titles
def create_banner(user_data, template_url, platform):
    # Download the template image from the URL
    response = requests.get(template_url)
    template_image = Image.open(BytesIO(response.content))
    
    # Set gap between logos
    gap = 150

    # Get logos and stock titles
    logos = user_data['logos']
    stock_titles = user_data['stock_titles']

    # Offsets and properties for text, logo placement, and logo size by platform
    platform_offsets = {
        "Twitter": {"text_offset_x": 0, "text_offset_y": 0, "logo_offset_x": 0, "logo_offset_y": 50, "logo_size": 96, "font_scale": 0.6, "thickness": 2, "text_top_padding": 80},
        "LinkedIn": {"text_offset_x": 0, "text_offset_y": 10, "logo_offset_x": 0, "logo_offset_y": 40, "logo_size": 96, "font_scale": 0.6, "thickness": 2, "text_top_padding": 70},
        "Substack": {"text_offset_x": -40, "text_offset_y": 30, "logo_offset_x": -40, "logo_offset_y": 30, "logo_size": 48, "font_scale": 0.5, "thickness": 1, "text_top_padding": 20}
    }

    # Get platform-specific properties
    logo_size = platform_offsets[platform]["logo_size"]
    font_scale = platform_offsets[platform]["font_scale"]
    thickness = platform_offsets[platform]["thickness"]
    text_top_padding = platform_offsets[platform]["text_top_padding"]
    text_offset_x = platform_offsets[platform]["text_offset_x"]
    text_offset_y = platform_offsets[platform]["text_offset_y"]
    logo_offset_x = platform_offsets[platform]["logo_offset_x"]
    logo_offset_y = platform_offsets[platform]["logo_offset_y"]

    # Calculate total width occupied by all logos and gaps
    total_logos_width = len(logos) * logo_size + (len(logos) - 1) * gap

    # Start position of the first logo (center all logos horizontally)
    start_x = (template_image.width - total_logos_width) // 2 + 50

    # Draw logos
    for i, logo_url in enumerate(logos):
        try:
            # Download and open each logo
            response = requests.get(logo_url)
            logo = Image.open(BytesIO(response.content))

            # Resize logo
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            
            # Calculate position to paste the logo
            x = start_x + i * (logo_size + gap) + logo_offset_x
            y = (template_image.height - logo_size) // 2 + logo_offset_y  # Vertically centered
            
            # Paste the logo onto the banner
            if logo.mode == 'RGBA':
                template_image.paste(logo, (x, y), logo)
            else:
                template_image.paste(logo, (x, y))

        except Exception as e:
            print(f"Couldn't process logo {i + 1}: {str(e)}")

    # Convert PIL Image to OpenCV format for text rendering
    banner_cv = cv2.cvtColor(np.array(template_image), cv2.COLOR_RGB2BGR)

    # Set base font size based on platform
    ticker_spacing = 5

    # Load font
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Draw stock titles (names and tickers)
    for i, stock_title in enumerate(stock_titles):
        name, ticker = stock_title.split(' (')
        ticker = '(' + ticker  # Add the '(' back to the ticker

        # Calculate text positions (centered below the logo)
        text_x = start_x + i * (logo_size + gap) + logo_size // 2 + text_offset_x  # Center text with the logo
        
        # Calculate the height of the text
        name_size = cv2.getTextSize(name, font, font_scale, thickness)[0]
        ticker_size = cv2.getTextSize(ticker, font, font_scale, thickness)[0]
        total_text_height = name_size[1] + ticker_size[1] + ticker_spacing
        
        # Position the text just below the logo
        logo_bottom_y = (template_image.height + logo_size) // 2  # Y-coordinate of logo bottom
        text_y_name = logo_bottom_y + text_top_padding + text_offset_y
        text_y_ticker = text_y_name + name_size[1] + ticker_spacing

        # Center the name and ticker horizontally
        name_x = text_x - name_size[0] // 2
        ticker_x = text_x - ticker_size[0] // 2
        
        # Draw the name and ticker
        cv2.putText(banner_cv, name, (name_x, text_y_name), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        cv2.putText(banner_cv, ticker, (ticker_x, text_y_ticker), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    # Convert back to PIL Image for returning
    return Image.fromarray(cv2.cvtColor(banner_cv, cv2.COLOR_BGR2RGB))

# Configure and render Streamlit page
st.set_page_config(
    page_title="RhinoFolio",
    page_icon="🎞️",
    #layout="wide",
    initial_sidebar_state="auto"
    )
st.title("Social Media Banner Creator")
st.markdown(
    "This mini-app generates social media banners based on your latest stock analysis. Made by [RhinoInsight](https://twitter.com/rhinoinsight)."
)

# Fetch usernames from the Google Sheet
usernames = fetch_usernames()

# Add a search/selection option for the usernames
username = st.selectbox("Select or search for your Substack/Beehiiv/PersonalBlog handle (without @):", usernames)

# Get user template choice 
template_choice = st.selectbox("Choose a banner template:", ["Temp_1", "Temp_2", "Temp_3"])

# Define multiple template URLs for different platforms
TEMPLATE_URLS = {
    "Temp_1": [
        "https://ucarecdn.com/e68a294b-16bd-4552-a59b-00e49b1f7338/banner_temp1_twitter_substack.png",
        "https://ucarecdn.com/f34a04bf-c180-4358-9bb5-6adc3c655c60/banner_temp1_linkedin_substack.png",
        "https://ucarecdn.com/facfa1d1-6c8f-47f4-a390-053f2d20bbb9/banner_temp1_substack_emailheader.png" 
    ],
    "Temp_2": [
         "https://ucarecdn.com/735dae47-577a-4b29-a229-7e579eb5b6c9/banner_temp2_twitter_substack.png",
         "https://ucarecdn.com/4f77976e-bf2c-48ee-81d5-a5f684eb45b5/banner_temp2_linkedin_substack.png",
         "https://ucarecdn.com/e6ed0d6b-76a4-4aee-b3ec-01a360e93d3b/banner_temp2_substack_emailheader.png"
    ],
    "Temp_3": [
        "https://ucarecdn.com/34f8f4fe-5a0a-46e3-afd4-855339c1bbaf/banner_temp3_twitter_substack.png",
        "https://ucarecdn.com/363834b7-6e60-4666-8931-c154a59ef3cc/banner_temp3_linkedin_substack.png",
        "https://ucarecdn.com/6e838ce8-736d-4c3c-b2e9-c6b474b08d50/banner_temp3_substack_emailheader.png"
    ],
}

if st.button("Create Banner", type="primary"):
    st.markdown("""---""")
    if username:
        try:
            user_data = get_user_data(username)
            if user_data is None:
                st.error("Username not listed. Please make sure you have already submitted at least one stock analysis report to [Rhinoinvestory.com](https://rhinoinvestory.com/) before you create your customized banner.")
            else:
                # Get the selected template
                template_link = TEMPLATE_URLS[template_choice]

                # Create banners for Twitter and LinkedIn using the selected template
                platforms = ["Twitter", "LinkedIn", "Substack"]
                for i, platform in enumerate(platforms):
                    template = template_link[i]  # Use the corresponding template for each platform
                    banner = create_banner(user_data, template, platform)
                    
                    # Convert PIL Image to bytes
                    img_byte_arr = BytesIO()
                    banner.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Display the banner
                    st.subheader(f"{platform} Banner")
                    st.image(img_byte_arr, caption=f"{platform} Banner", use_column_width=True)
                    
                    # Provide download link
                    st.download_button(
                        label=f"Download {platform} Banner",
                        data=img_byte_arr,
                        file_name=f"{username}_{platform.lower()}_banner.png",
                        mime="image/png"
                    )
                
                st.success("Banners created successfully!")
                st.info("To use these banners:\n"
                        "1. Download the banner for each platform\n"
                        "2. Go to your profile settings on each platform\n"
                        "3. Look for an option to upload a custom header or banner\n"
                        "4. Upload the corresponding banner image\n\n"
                        "Note: The exact steps may vary depending on each platform's current interface.\n", icon="ℹ️") 
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}. Please try again later or contact support if the issue persists.")
    else:
        st.warning("Please enter your Substack/Beehiiv/PersonalBlog handle.")