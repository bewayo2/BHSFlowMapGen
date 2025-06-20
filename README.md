# Process Map Generator

A modern web application that converts text content into beautiful process flow and swimlane diagrams using GPT-4 and Graphviz.

## Features

- **AI-Powered Conversion**: Uses GPT-4 to intelligently convert text descriptions into structured process tables
- **Two Diagram Types**: 
  - Process Flow diagrams with standard notation (Start, Process, Decision, Subprocess, End)
  - Swimlane diagrams with function and phase organization
- **Interactive UI**: Modern, responsive web interface
- **Export Options**: Download diagrams as SVG or DOT files
- **Real-time Preview**: See your diagrams rendered instantly
- **Single File Frontend**: All frontend code is in one HTML file with embedded CSS and JavaScript

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd process-map-generator
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=5000
   ```

## Usage

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

## How to Use

1. **Select Diagram Type**: Choose between "Process Flow" or "Swimlane Map"

2. **Enter Content**: Paste your process description into the text area
   - Example: "First, we create a course module. Then it goes through review. If it passes, we publish it. If not, we address feedback and send it back to review."

3. **Convert to Table**: Click "Convert to Table" to generate a structured table using GPT-4

4. **Generate Diagram**: Click "Generate Diagram" to create a visual representation using Graphviz

5. **Download**: Export your diagram as SVG or DOT file

## API Endpoints

### POST /api/convert
Converts text content to structured table format.

**Request Body:**
```json
{
  "content": "Your process description",
  "diagramType": "process-flow" | "swimlane"
}
```

**Response:**
```json
{
  "success": true,
  "tableData": [...],
  "rawTable": "JSON string"
}
```

### POST /api/generate-diagram
Generates Graphviz DOT code from table data.

**Request Body:**
```json
{
  "tableData": [...],
  "diagramType": "process-flow" | "swimlane"
}
```

**Response:**
```json
{
  "success": true,
  "dotCode": "digraph {...}"
}
```

## Table Formats

### Process Flow Format
| Process Step ID | Process Step Description | Next Step ID | Connector Label | Shape Type | Alt Text |
|----------------|------------------------|--------------|----------------|------------|----------|
| P100 | Create course module | P200 | | Start | |
| P200 | Module passes review? | P300,P400 | Yes,No | Decision | |

### Swimlane Format
| Process Step ID | Process Step Description | Next Step ID | Connector Label | Shape Type | Function | Phase | Alt Text |
|----------------|------------------------|--------------|----------------|------------|----------|-------|----------|
| P100 | Get course requirements | P200 | | Start | Project Managers | Plan | |
| P200 | Create course module | P300 | | Document | Writers | Review | |

## Technologies Used

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI**: OpenAI GPT-4
- **Diagrams**: Graphviz (DOT language)
- **Styling**: CSS3 with modern gradients and animations
- **HTTP Client**: Axios (CDN)
- **Notifications**: Custom toast notifications

## Project Structure

```
process-map-generator/
├── app.py                 # Flask server with OpenAI integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── static/
│   └── index.html         # Complete frontend (HTML + CSS + JS)
└── README.md
```

## Development

- **Run**: `python app.py` (Flask development server)
- **Debug**: Set `debug=True` in app.py for development mode

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PORT`: Server port (default: 5000)

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file**:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PORT=5000
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open browser** to `http://localhost:5000`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub. 