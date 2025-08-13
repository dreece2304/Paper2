macro "Extract Grating Data [7]" {
    // ====== INITIAL SETUP ======
    roiManager("reset");
    title = getTitle();
    getPixelSize(unit, pixelWidth, pixelHeight);

    // Detect dose from filename
    dose = 0;
    if (indexOf(title, "5000") >= 0) dose = 5000;
    else if (indexOf(title, "7000") >= 0) dose = 7000;
    else if (indexOf(title, "15000") >= 0) dose = 15000;
    else if (indexOf(title, "20000") >= 0) dose = 20000;

    print("\\Clear");
    print("=== Extracting Data from " + title + " ===");
    print("Dose: " + dose + " µC/cm²");

    // ====== STEP 1: SELECT GRATING REGION ======
    setTool("rectangle");
    waitForUser("Step 1: Select Grating", 
        "Draw a rectangle around all 5 lines (tight, no extra space).\nClick OK when done.");

    if (selectionType() != 0) {
        exit("Please draw a rectangular selection for the grating.");
    }

    Roi.getBounds(gx, gy, gwidth, gheight);
    roiManager("add");
    roiManager("rename", "grating");

    print("Grating size: " + gwidth + " x " + gheight + " px");
    print("Line length: " + d2s(gwidth * pixelWidth, 2) + " µm");

    // ====== STEP 2: SELECT BACKGROUND REGION ======
    waitForUser("Step 2: Select Background", 
        "Draw a rectangle over a clean background (no features).");

    if (selectionType() != 0) {
        roiManager("add");
        roiManager("rename", "background");

        // Select background ROI by index to avoid selection errors
        roiIndex = roiManager("count") - 1;
        roiManager("select", roiIndex);
        run("Measure");
        bgMean = getValue("Mean");
        bgStd = getValue("StdDev");
        
        print("Background: mean=" + d2s(bgMean, 1) + ", std=" + d2s(bgStd, 1));
    } else {
        exit("No valid background selection made.");
    }

    // ====== STEP 3: PROFILE ACROSS GRATING HEIGHT ======
    roiManager("select", "grating");
    run("Duplicate...", "title=temp");
    selectWindow("temp");

    // Optional preprocessing: subtract background to enhance contrast
    // run("Subtract Background...", "rolling=50");

    profile = newArray(gheight);
    for (y = 0; y < gheight; y++) {
        sum = 0;
        for (x = 0; x < gwidth; x++) {
            sum += getPixel(x, y);
        }
        profile[y] = sum / gwidth;
    }
    close("temp");

    // Display profile
    Plot.create("Vertical Profile - Check for 5 Peaks", "Y Position (µm)", "Intensity");
    for (i = 0; i < gheight; i++) {
        Plot.add("line", i * pixelHeight, profile[i]);
    }
    Plot.show();

    // ====== STEP 4: SAVE DATA ======
    dir = getDirectory("Choose where to save data");

    // Save profile
    f = File.open(dir + "profile_" + dose + ".csv");
    print(f, "pixel,y_um,intensity,bg_mean,bg_std");
    for (i = 0; i < profile.length; i++) {
        print(f, i + "," + (i * pixelHeight) + "," + profile[i] + "," + bgMean + "," + bgStd);
    }
    File.close(f);

    // Save metadata
    f = File.open(dir + "metadata_" + dose + ".csv");
    print(f, "parameter,value");
    print(f, "dose," + dose);
    print(f, "pixel_width," + pixelWidth);
    print(f, "pixel_height," + pixelHeight);
    print(f, "grating_width_px," + gwidth);
    print(f, "grating_height_px," + gheight);
    print(f, "grating_width_um," + (gwidth * pixelWidth));
    print(f, "grating_height_um," + (gheight * pixelHeight));
    print(f, "bg_mean," + bgMean);
    print(f, "bg_std," + bgStd);
    File.close(f);

    // Save ROIs
    roiManager("save", dir + "ROIs_" + dose + ".zip");

    print("\n=== Data Saved ===");
    print("  profile_" + dose + ".csv");
    print("  metadata_" + dose + ".csv");
    print("  ROIs_" + dose + ".zip");
}
