# Google Play Reviews CLI with AI Integration

A command-line application for managing Google Play app reviews using the Google Play Developer Reply-to-Reviews API with AI-powered automatic response generation.

## Features

- 📋 List the latest app reviews with detailed information
- 💬 Reply to specific reviews manually
- 🤖 **AI-powered automatic responses** using Google Gemini
- 🌍 **Multilingual support** - responds in the same language as the review
- 📊 **Smart response rules** based on rating (1-5 stars)
- 🎨 Colored and formatted output (using Rich library)
- 🔐 Secure authentication using service account credentials
- ⚡ Error handling with clear logging
- 🏗️ Modular code structure
- 📈 **AI statistics and reply history tracking**
- 🧪 **Dry-run mode** for testing AI responses

## Prerequisites

- Python 3.10 or higher
- Google Play Console account with API access
- Service account with appropriate permissions
- **Google Gemini API key** (for AI features)

## Required Permissions

Your service account needs the following permissions in Google Play Console:

1. **View app information and download bulk reports**
2. **Reply to reviews** (for the reply functionality)

### Setting up Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Play Developer API
4. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Give it a name and description
   - Grant the service account the necessary roles
5. Create and download the JSON key file
6. Rename the downloaded file to `service_account.json` and place it in the project root

### Granting Play Console Access

1. Go to [Google Play Console](https://play.google.com/console/)
2. Navigate to Setup > API access
3. Link your Google Cloud project
4. Grant access to your service account with the required permissions

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Place your `service_account.json` file in the project root directory
4. Set your Google Gemini API key as an environment variable:

```bash
# Windows
set GEMINI_API_KEY=your_gemini_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_gemini_api_key_here
```

### Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Set it as an environment variable as shown above

## Usage

### Basic Commands

#### List Reviews
```bash
python main.py --package com.example.app list
```

#### List More Reviews
```bash
python main.py --package com.example.app list --max-results 10
```

#### Reply to a Review
```bash
python main.py --package com.example.app reply REVIEW_ID "Thank you for your feedback!"
```

#### AI-Powered Auto-Reply
```bash
# Generate AI responses for latest 5 reviews (dry run - no posting)
python main.py --package com.example.app --enable-ai auto-reply --dry-run

# Actually post AI responses to reviews
python main.py --package com.example.app --enable-ai auto-reply

# Process more reviews
python main.py --package com.example.app --enable-ai auto-reply --max-results 10
```

#### AI Statistics and History
```bash
# Show AI response statistics
python main.py --package com.example.app --enable-ai ai-stats

# Show recent AI reply history
python main.py --package com.example.app --enable-ai history --limit 20
```

### Command Line Options

- `--package`, `-p`: Package name of your app (required)
- `--max-results`, `-n`: Maximum number of reviews to display (default: 5)

### Examples

```bash
# List 5 latest reviews
python main.py --package com.mycompany.myapp list

# List 10 latest reviews
python main.py --package com.mycompany.myapp list --max-results 10

# Reply to a specific review
python main.py --package com.mycompany.myapp reply gp:AOqpTOE5Xy4 example "Thanks for the feedback! We'll look into this issue."

# Get help
python main.py --help
```

## Project Structure

```
google-play-reviews-cli/
├── main.py                 # CLI entry point
├── auth.py                 # Authentication module
├── reviews.py              # Reviews management module
├── requirements.txt        # Python dependencies
├── service_account.json    # Google service account credentials (you need to add this)
└── README.md              # This file
```

## Error Handling

The application includes comprehensive error handling:

- **Authentication errors**: Clear messages when service account file is missing or invalid
- **API errors**: Detailed error messages from Google Play Developer API
- **Network errors**: Graceful handling of connection issues
- **Input validation**: Proper validation of command line arguments

## Output Formatting

The application uses the Rich library for beautiful terminal output:

- ✅ Success messages in green
- ❌ Error messages in red
- ℹ️ Info messages in blue
- ⚠️ Warning messages in yellow
- 📊 Formatted tables for review listings

If Rich is not available, the application falls back to simple text output.

## Troubleshooting

### Common Issues

1. **"Service account file not found"**
   - Ensure `service_account.json` is in the project root
   - Check the file name is exactly `service_account.json`

2. **"Authentication failed"**
   - Verify your service account has the correct permissions
   - Check that the Google Play Developer API is enabled
   - Ensure the service account is linked in Play Console

3. **"Package not found"**
   - Verify the package name is correct
   - Ensure the app is published and has reviews
   - Check that the service account has access to the app

4. **"Permission denied"**
   - Verify the service account has "Reply to reviews" permission
   - Check that the app is in the correct state (published)

### Getting Help

Run the application with `--help` to see all available options:

```bash
python main.py --help
```

## Development

### Code Structure

- **`auth.py`**: Handles Google Play Developer API authentication
- **`reviews.py`**: Contains review listing and replying functionality
- **`main.py`**: CLI interface and command handling

### Adding New Features

1. Add new methods to the `GooglePlayReviews` class in `reviews.py`
2. Add corresponding CLI commands in `main.py`
3. Update the argument parser as needed

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please check the troubleshooting section above or create an issue in the project repository.
