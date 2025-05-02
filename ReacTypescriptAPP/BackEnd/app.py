# ... existing code ...

# Import the second stage classification function
from analyze_complaints_secondstage import classify_complaints

# Add this new route for the second stage classification
@app.route('/api/analyze-complaints/classtype', methods=['GET'])
def get_classified_complaints():
    """API endpoint to get classified complaints"""
    result = classify_complaints()
    return jsonify(result)