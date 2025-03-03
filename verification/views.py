from django.shortcuts import render
from django.http import JsonResponse
from phi.agent import Agent
from phi.tools.googlesearch import GoogleSearch
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo

from .models import Product, VerificationResult
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Gemini API key
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize agents
image_analyzer = Agent(
    name="Image Analyzer",
    role="Analyzes product images to detect counterfeit products.",
    model=Gemini(id="gemini-1.5-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "Analyze the uploaded product image to detect signs of counterfeiting.",
        "Compare the image with authentic product samples.",
        "Provide a detailed report on whether the product is likely counterfeit.",
        "Analyze the provided product image for visual features, including logos, packaging, labels, and overall quality.",
        "Identify any anomalies, inconsistencies, or signs of tampering.",
        "Compare the visual features with known authentic product images (if available).",
        "Pay close attention to detail, such as font, color, and texture.",
        "Report any visual discrepancies or potential counterfeit indicators.",
        "Compare the retrieved database information and image analysis results.",
        "Assess the consistency and reliability of the data.",
        "If the database information and image analysis match known authentic product details, determine the product as 'Original'.",
        "If discrepancies or counterfeit indicators are found, determine the product as 'Fake'.",
        "Generate a confidence score based on the strength of the evidence.",
        "Provide a clear and concise explanation of your reasoning, citing specific evidence.",
        "If there is a mix of evidence, carefully weight the evidence, and give a best guess with a lower confidence score.",


    ],
    show_tool_calls=False,
    markdown=True,
)

barcode_scanner = Agent(
    name="Barcode Scanner",
    role="Scans and verifies product barcodes or serial numbers.",
    tools=[GoogleSearch(), DuckDuckGo()],
    model=Gemini(id="gemini-1.5-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "Given a barcode or the barcode serial number, search for the product name, company and so on.",
        "If the input is a string, assume it is the barcode or serial number. Extract the raw numerical value.",
        "If the input is an image, use image processing techniques to identify and extract the barcode. If no barcode is found, state 'Barcode not found'.",
        "Verify the product's authenticity using other online databases too.",
        "Provide a report on whether the product is original or counterfeit.",
        "Query online product databases (e.g., Open Food Facts, GS1) using the extracted barcode or serial number.",
        "Retrieve product details, including name, manufacturer, specifications, and any available images."


    ],
    show_tool_calls=False,
    markdown=True,
)

web_searcher = Agent(
    name="Web Searcher",
    role="Searches the web for additional product information.",
    tools=[GoogleSearch(), DuckDuckGo()],
    model=Gemini(id="gemini-1.5-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "Search the web for product details, reviews, and counterfeit reports.",
        "Provide additional context to help verify the product's authenticity."
    ],
    show_tool_calls=False,
    markdown=True,
)

counterfeit_detection_team = Agent(
    name="Counterfeit Detection Team",
    team=[image_analyzer, barcode_scanner, web_searcher],
    model=Gemini(id="gemini-1.5-flash", api_key=GEMINI_API_KEY),
    instructions=[
        "you are an expert product verification agent. Your purpose is to determine whether a product is genuine or counterfeit based on provided information.",
        "You will receive either a product's serial number/barcode or an image of the product. You may receive both.",
        "Don't show the processes, just go straight to the point.",
        "You should always display response in summary.",
        "Just display, name of product and company, it is original or counterfeit",
        "If is just the barcode serial number, process on the barcode only and verify whether the product is original or counterfeit",
        "If is just and image,process the image only and verify whether the product is original or counterfeit",
        "If is an image, analyze the uploaded product image using the Image Analyzer.",
        "If a barcode or serial number is provided, verify it using the Barcode Scanner.",
        "Use the Web Searcher to gather additional information about the product.",
        "Provide a detailed report with evidence to support your conclusion.",
        "It is either the product image or the barcode serial number. So, process them differently.",
        "Provide a clear 'Original' or 'Fake' determination.",
        "Include a confidence score (e.g., 'Confidence: 85%').",
        "Provide a detailed explanation of your reasoning, citing specific evidence.",
        "If the product is fake, highlight the discrepancies and potential counterfeit indicators.",
        "Prioritize information from official databases (e.g., GS1, manufacturer websites) when available.",
        "Treat image analysis as supplementary evidence, especially for visual discrepancies.",
        "Prioritize information from official databases (e.g., GS1, manufacturer websites) when available.",
        "Treat image analysis as supplementary evidence, especially for visual discrepancies."
        
    ],
    show_tool_calls=False,
    markdown=True,
)
def verify_product(request):
    """Handle product verification requests."""
    if request.method == "POST":
        barcode = request.POST.get("barcode")
        image_file = request.FILES.get("image")

        if not barcode and not image_file:
            return JsonResponse({"error": "Please provide a barcode or image."}, status=400)

        
        # Process the uploaded image
        if image_file:
            # Save the file to a temporary location
            with image_file.open('rb') as f:
                image_data = f.read()

            # Example: Process the image (e.g., resize or analyze)
            try:
                image = Image.open(BytesIO(image_data))
                image.verify()  # Verify that the file is a valid image
                image = Image.open(BytesIO(image_data))  # Reopen the image for processing
                result = f"Image processed successfully. Size: {image.size}"
            except Exception as e:
                result = f"Invalid image file: {str(e)}"
        else:
            result = "No image provided."
        # Run the counterfeit detection team
        response = counterfeit_detection_team.run(
            f"Analyze this product image: {image_file}" if image_file else f"Verify the authenticity of the product with barcode: {barcode}. Provide the product name, company, and verification result"
        )

        # Extract the result
        result = response.content if response else "No response from the verification system."
        
        verification_result = VerificationResult(
            barcode=barcode,
            image=None,  # Save the image path
            is_authentic=True,  # Replace with actual verification logic
            details=result,
        )
        verification_result.save()

        

        # Pass the result to the template
        return JsonResponse({"result": result})
    return render(request, 'home.html')

    # return JsonResponse({"error": "Invalid request method."}, status=405)

# def home(request):
#     return render(request, 'home.html')    

def index(request):
    return render(request, 'index.html')  

def report(request):
    return render(request, 'report.html')  