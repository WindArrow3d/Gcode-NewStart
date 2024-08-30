# Gcode-NewStart
Gcode NewStart is a tool designed to help the 3d printing community. It helps save failed prints when there is a clear failure layer and allows the user to begin printing again starting at a layer of their choice.

First thing first, this tool can damage your printer, your computer, or cause bodily injury. Any user attempting to use this tool is doing so at their own risk. I am not responsible for anything bad that happens. I make no guarantees whatsoever. 
I don't know python. This tool is written in python... "How is that?" you ask? 90% of the code was written by ChatGPT. 9% was written by a close friend of mine, fixing the weirdness ChatGPT had going on and made the tool useable. The last 1% was me, making minor adjustments to already useable code. I'm positive the code is not written well or follows any best practices. It could cause your computer to crash or worse. I cannot take responsibility in the event the tool generates any type of negative consequences. 

That being said, I am happy to share this with the 3D printing community. I have benefited immensely from opensource 3D printing contributions, and this is my way of trying to give a tiny bit back, using my extremely limited skillset. Please feel free to make this tool better. If you find something broken, or would like to see a feature added, please create an issue or bug, but know that I have zero intention of continuing to support this project. It does exactly what I need it to, and I'm not suited to expand it. By entering an issue, you will help others see what is potentially broken and give the community a heads-up on your experience with the tool. Who knows, maybe someone much more talented than me will fork the project and fix/add any items in the issues. 

# How it works:

Gcode NewStart is a script that is manually run by the user. It asks for some user inputs:  
* The original gcode file of the failed print (select the gcode file)  
* Desired Nozzle temperature (enter temp in degrees C)  
* Desired Bed temperature (enter temp in degrees C)  
* Desired Part Cooling Fan speed as a percentage (enter speed percentage)  
* If you would like to load the bed mesh from memory (Y or N)  
* A Pre-Purge amount in mm (enter the amount of filament in mm to extrude immediately before the print starts)  
* Select the layer number/Z height that you would like to restart printing. (select the checkbox you would like the print to restart at)  
  
## What it does with that information:  
* Gcode NewStart will analyze the gcode file and automatically detect the slicer used to generate the original gcode (Gcode NewStart currently only supports Cura, Orca Slicer, and Prusa Slicer)  
* It finds every layer change so the user can select the one that suits them best.  
* All start gcode and layers prior to the one selected are omitted.  
* New start gcode is added based on the user selections made.  
* It then saves the gcode to a new file in the same location as the original file. The original file is not altered in any way. The new filename is structured:
	* “original file name”-NEWSTART-LAYER***.gcode  

# Criteria:  
* I think this will only work with gcode sliced for Marlin. I've only used Marlin and it's all I know. I don't advise using this for anything other than Marlin unless you know exactly what you are doing.  
* I only use Windows. No idea how/if this will run on other operating systems.  
* The print must remain stuck to the bed.  
	* If the bed has cooled and the print has released from the bed, you're out of luck using the Gcode NewStart method.  
* The printer must accurately maintain its x,y,z positions.  
	* The printer must know where the print head is exactly in relation to the print. Otherwise, it will not accurately restart printing in the correct location. This means that the axes' homing operations used prior to the original print must be maintained into the Gcode NewStart gcode file.  
	* Gcode NewStart does not re-home the axes. This is because the print is still on the bed and the likelihood of crashing the hot end into the print is high.  


# How to use it:  
* You go to check on your print, and disaster has struck! The nozzle is moving around in midair and is apparently clogged! Never fear, Gcode NewStart is here!  
* PAUSE the print. This will move the print head to its parked position, maintain the bed temperature, and maintain the positions of the axes. The stepper motors should remain engaged.  
* DON'T MOVE THE X, Y or Z AXES BY HAND  
* DON'T REMOVE THE PRINT FROM THE BED  
* DON’T RE-HOME THE AXES  
* If you need to clear a clog or change the nozzle, this is the time to do it. You need to be extremely careful not to upset the axes' positions or the print. If either of those things happen, Gcode NewStart won't work and could potentially cause the print head to collide with the print or the hard limits of the axes. Feel free to set the nozzle temperature to what you need to clear the clog.  
* Go to your computer and run Gcode_NewStart_Cura_Orca_Prusa_V9.exe.  
* Select the exact gcode file that was printing, when prompted with the file explorer window titled: “Select the original G-code file”.  
* Enter the desired Nozzle temperature (C), desired Bed temperature (C), desired Part Cooling Fan speed (%), if you would like to load the bed mesh from memory (y/n), and Pre-Purge amount (mm).
	* A note about Pre-Purge:  
		* This will extrude the entered distance of filament immediately before the print starts. This is meant to build some pressure in the nozzle right before the print starts to counteract potential under extrusion. I've found that 0.2mm works well for Bowden printers with 0.4mm nozzles. Your printer may require a higher or lower amount- testing and experimenting is advised.
* Select the correct layer to restart on.  
	* This can be tricky. You’ll need the ability to accurately determine the layer # or exact layer height of the last “good” layer.  
		* This can be done using calipers and measuring the height of the print from the bed surface.  
	* The layer you want to select is NOT the layer you measured. You need to select the layer above the layer you measured.  
		* Example: You measured the height of the print to be 10mm.  
		* You find the layer # with a z height of 10mm (or as close as possible) from the list of available layers in the application, and select the next layer higher.  
		* Let’s say you locate layer 50 with a height of 10mm. You’ll need to select the next layer (layer 51) with a height of 10.2mm (assuming our example used a 0.2mm layer height).  
* Once you’ve selected the correct layer number check box, press the ok button and the new file will be created and placed in the same location as the original gcode file.  
* Prep the file to be uploaded, but don’t start the print yet (chose the method you normally use):  
	* SD card:  
		* Place the new file on an SD card.  
	* OctoPrint:  
		* Upload the gcode file to OctoPrint.  
* This step will need to be completed quickly.  
	* CANCEL/STOP the print.  
	* Quickly start the new gcode. This is a critical moment. If the bed cools too much, you’ll lose adhesion and it won’t be recoverable. If any of the axes move between canceling the old print and starting the new gcode, it won’t be recoverable.  
* Once the bed and nozzle temperatures settle, the print will start at the beginning of the layer you selected.  
