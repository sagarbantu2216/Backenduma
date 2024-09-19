import os
import matplotlib
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import numpy as np

# Set the matplotlib backend to Agg, which is non-GUI
matplotlib.use('Agg')

def chestScanPrediction(image_path):
    classes_dir = ["Adenocarcinoma", "Large cell carcinoma", "Normal", "Squamous cell carcinoma"]

    # Load the pre-trained model
    model_eff = load_model("ct_incep_best_model.hdf5")

    # Load and preprocess the image
    img = image.load_img(image_path, target_size=(350, 350))
    img_array = image.img_to_array(img) / 255.0
    img_batch = np.expand_dims(img_array, axis=0)

    # Predict the class of the image
    pred_probs = model_eff.predict(img_batch)[0]
    pred_class_index = np.argmax(pred_probs)

    # Check the confidence of the prediction
    if pred_probs[pred_class_index] < 0.9:
        result = ("Unknown", pred_probs)
    else:
        pred_label = classes_dir[pred_class_index]
        result = (pred_label, pred_probs)

        # Save the plot
        plt.imshow(img)
        plt.title(f"Predicted Label: {pred_label}")
        plt.axis('off')  # Hide axes
        
        # Create the directory if it doesn't exist
        plot_filename = "static/predicted_image.png"
        if not os.path.exists("static"):
            os.makedirs("static")
        plt.savefig(plot_filename)
        plt.close()  # Close the figure to free up resources

        return plot_filename, result
    return None, None
