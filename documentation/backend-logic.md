# Backend Logic for Try-On API

Okay, assuming the frontend, backend infrastructure (Flask app, DB connection, file upload endpoint, static file serving), and database are all set up, here is the numeric list focusing *only* on the **core logic steps required within the `/api/tryon` backend endpoint** after it has received the request and loaded both the user image and clothing item image into memory (e.g., as Pillow `user_image` and `clothing_image` objects):

1. **Prepare User Image for Detection:** Convert the loaded user Pillow image (RGBA) into the format required by your chosen detection library (e.g., an RGB NumPy array for MediaPipe).
2. **Detect Body/Pose Landmarks:** Initialize and run your chosen detection library (e.g., `mediapipe.solutions.pose.process()`) on the prepared user image data.
3. **Extract Key Coordinates:** From the detection results, extract the specific coordinates (and potentially visibility/confidence scores) of the required landmarks (e.g., left/right shoulders, left/right hips). Include error handling if crucial landmarks are not detected reliably.
4. **Calculate Overlay Parameters:** Using the extracted landmark coordinates and the original user image dimensions, calculate the necessary parameters for the overlay:
    * Target width for the clothing image.
    * Target X, Y coordinates (e.g., top-center or center point) on the user image where the clothing should be placed.
5. **Resize Clothing Image:** Resize the loaded clothing Pillow image (which should have transparency) to the calculated `target_width`, ensuring the aspect ratio is maintained.
6. **Overlay Images:** Paste the resized clothing image onto the user Pillow image at the calculated target coordinates. Ensure you use the alpha channel of the clothing image as the mask for proper transparency (`Image.paste(clothing, box, mask=clothing)`).
7. **Save Result Image:** Generate a unique filename for the output. Construct the full save path within your `UPLOAD_FOLDER`. Save the final composite Pillow image (the user image with the overlay) to this path, preferably as a PNG to preserve any transparency.
8. **Generate Result URL:** Create the relative URL path (e.g., `/uploads/unique_result_name.png`) corresponding to the saved result image, which can be served by your static file route.

These 8 steps represent the core image processing pipeline within your `/api/tryon` function, transforming the input images into the final try-on result.
