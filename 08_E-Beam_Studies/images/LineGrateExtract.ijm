macro "Analyze SEM Line Gratings with Plugins [F4]" {
    // Enhanced macro using MorphoLibJ and BAR Find Peaks
    // Works with both bright (5000, 7000) and dark (15000, 20000) lines
    
    requires("1.53c");
    
    // Check for required plugins
    if (!checkPlugin("MorphoLibJ")) {
        showMessage("Please install MorphoLibJ from IJPB-plugins update site");
        exit();
    }
    
    // Get image properties
    title = getTitle();
    getPixelSize(unit, pixelWidth, pixelHeight);
    getDimensions(width, height, channels, slices, frames);
    
    // Determine dose and line type
    dose = 0;
    brightLines = true;
    if (indexOf(title, "5000") >= 0) { dose = 5000; brightLines = true; }
    else if (indexOf(title, "7000") >= 0) { dose = 7000; brightLines = true; }
    else if (indexOf(title, "15000") >= 0) { dose = 15000; brightLines = false; }
    else if (indexOf(title, "20000") >= 0) { dose = 20000; brightLines = false; }
    
    print("\\Clear");
    print("=== Advanced SEM Line Grating Analysis ===");
    print("Image: " + title);
    print("Dose: " + dose + " µC/cm²");
    print("Line type: " + (brightLines ? "Bright (crosslinked)" : "Dark (carbonized)"));
    
    // Create output directory
    dir = getDirectory("Choose output directory");
    outDir = dir + "Analysis_" + dose + "uC/";
    File.makeDirectory(outDir);
    
    // Select grating region
    setTool("rectangle");
    waitForUser("Draw rectangle around entire grating area, then click OK");
    
    if (selectionType() != 0) exit("Please make a rectangular selection");
    
    Roi.getBounds(gx, gy, gwidth, gheight);
    run("Duplicate...", "title=working");
    
    // ========== METHOD 1: MorphoLibJ Directional Filtering ==========
    print("\n--- MorphoLibJ Analysis ---");
    selectWindow("working");
    run("Duplicate...", "title=morpho");
    
    // Apply directional filter to enhance horizontal lines
    run("Directional Filtering", "type=Max operation=Opening line_length=20 direction=32 direction_number=180");
    rename("directional_filtered");
    
    // Morphological gradient for edge detection
    selectWindow("working");
    run("Duplicate...", "title=gradient");
    run("Morphological Filters", "operation=Gradient element=Square radius=1");
    saveAs("Tiff", outDir + "morphological_gradient.tif");
    
    // ========== METHOD 2: Enhanced Profile Analysis ==========
    print("\n--- Profile Analysis with Find Peaks ---");
    selectWindow("working");
    
    // Get vertical profile (average across width)
    makeRectangle(0, 0, gwidth, gheight);
    profile = getProfile();
    
    // Create plot for Find Peaks
    Plot.create("Vertical Profile", "Y Position", "Intensity", profile);
    Plot.show();
    
    // Use Find Peaks if available
    if (checkPlugin("Find_Peaks")) {
        // Adjust parameters based on line type
        if (brightLines) {
            run("Find Peaks", "min._peak_amplitude=20 min._peak_distance=10 min._value=NaN max._value=NaN list");
        } else {
            // For dark lines, we'll invert the profile first
            run("Find Peaks", "min._peak_amplitude=20 min._peak_distance=10 min._value=NaN max._value=NaN exclude list");
        }
        
        // Get peaks from results
        nPeaks = getValue("results.count");
        peaks = newArray(nPeaks);
        for (i = 0; i < nPeaks; i++) {
            peaks[i] = getResult("X1", i);
        }
        print("Find Peaks detected " + nPeaks + " lines");
    } else {
        // Fallback to simple peak detection
        peaks = simplePeakDetection(profile, brightLines);
        print("Simple detection found " + peaks.length + " lines");
    }
    
    // ========== METHOD 3: MorphoLibJ Region Analysis ==========
    print("\n--- Binary Region Analysis ---");
    selectWindow("working");
    run("Duplicate...", "title=binary");
    
    // Threshold based on line type
    if (brightLines) {
        setAutoThreshold("Default dark");
    } else {
        setAutoThreshold("Default");
    }
    run("Convert to Mask");
    
    // Clean up binary image
    run("Median...", "radius=1");
    
    // Analyze regions
    run("Analyze Regions", "area perimeter circularity euler_number bounding_box centroid equivalent_ellipse ellipse_elong. convexity max._feret oriented_box oriented_box_elong. geodesic tortuosity max._inscribed_disc average_thickness geodesic_elong.");
    
    // Save region results
    saveAs("Results", outDir + "region_analysis.csv");
    
    // ========== Detailed Line-by-Line Analysis ==========
    print("\n--- Detailed Line Measurements ---");
    selectWindow("working");
    
    Table.create("Line_Measurements");
    row = 0;
    
    // Analyze each detected line
    for (i = 0; i < peaks.length; i++) {
        lineY = peaks[i] + gy;
        
        // Extract line region
        lineHeight = 20;
        makeRectangle(gx, lineY - lineHeight/2, gwidth, lineHeight);
        run("Duplicate...", "title=line_" + i);
        
        // Get horizontal profile across line
        makeLine(0, lineHeight/2, gwidth, lineHeight/2);
        profile = getProfile();
        
        // Line width analysis using MorphoLibJ
        selectWindow("line_" + i);
        run("Duplicate...", "title=line_binary");
        setAutoThreshold("Default");
        run("Convert to Mask");
        
        // Distance map for width measurement
        run("Distance Map", "distances=[Chebyshev (1,1,1)] output=[16 bits] normalize");
        rename("distance_map");
        
        // Get maximum distance (half width)
        getRawStatistics(nPixels, mean, min, max, std);
        estimatedWidth = max * 2 * pixelWidth;
        
        // Profile analysis for edge quality
        selectWindow("line_" + i);
        Array.getStatistics(profile, pMin, pMax, pMean, pStd);
        
        // Edge detection using gradient
        edgeGradient = newArray(profile.length - 1);
        maxGradient = 0;
        for (j = 0; j < profile.length - 1; j++) {
            edgeGradient[j] = abs(profile[j+1] - profile[j]);
            if (edgeGradient[j] > maxGradient) maxGradient = edgeGradient[j];
        }
        
        // Calculate metrics
        contrast = (pMax - pMin) / (pMax + pMin);
        edgeSharpness = maxGradient / (pMax - pMin);
        
        // Add to results table
        Table.set("Line_Number", row, i + 1);
        Table.set("Y_Position", row, lineY);
        Table.set("Width_" + unit, row, estimatedWidth);
        Table.set("Mean_Intensity", row, pMean);
        Table.set("StdDev_Intensity", row, pStd);
        Table.set("Contrast", row, contrast);
        Table.set("Edge_Sharpness", row, edgeSharpness);
        Table.set("Dose_uC/cm2", row, dose);
        
        close("line_" + i);
        close("line_binary");
        close("distance_map");
        row++;
    }
    
    // Calculate pitch statistics
    if (peaks.length > 1) {
        pitches = newArray(peaks.length - 1);
        for (i = 0; i < peaks.length - 1; i++) {
            pitches[i] = (peaks[i+1] - peaks[i]) * pixelHeight;
        }
        Array.getStatistics(pitches, minPitch, maxPitch, meanPitch, stdPitch);
        
        print("\n=== Pitch Analysis ===");
        print("Mean pitch: " + d2s(meanPitch, 3) + " " + unit);
        print("Std deviation: " + d2s(stdPitch, 3) + " " + unit);
        print("CV: " + d2s(stdPitch/meanPitch*100, 1) + "%");
        print("Min pitch: " + d2s(minPitch, 3) + " " + unit);
        print("Max pitch: " + d2s(maxPitch, 3) + " " + unit);
        
        // Add summary statistics
        Table.set("Mean_Pitch_" + unit, 0, meanPitch);
        Table.set("Pitch_StdDev_" + unit, 0, stdPitch);
        Table.set("Pitch_CV_%", 0, stdPitch/meanPitch*100);
    }
    
    Table.save(outDir + "line_measurements.csv");
    
    // Create visualization
    selectWindow("working");
    run("Duplicate...", "title=visualization");
    run("Enhance Contrast", "saturated=0.35");
    
    // Overlay detected lines
    setColor("red");
    setLineWidth(1);
    for (i = 0; i < peaks.length; i++) {
        Overlay.drawLine(0, peaks[i], gwidth, peaks[i]);
        Overlay.add;
        Overlay.drawString("" + (i+1), 5, peaks[i] - 2);
        Overlay.add;
    }
    Overlay.show;
    
    saveAs("Tiff", outDir + "annotated_lines.tif");
    
    print("\n=== Analysis Complete ===");
    print("Results saved to: " + outDir);
    
    // Cleanup
    close("working");
    close("morpho");
    close("binary");
    close("visualization");
    close("directional_filtered");
}

// Helper function to check if plugin is installed
function checkPlugin(pluginName) {
    list = getList("plugins");
    for (i = 0; i < list.length; i++) {
        if (indexOf(list[i], pluginName) >= 0) return true;
    }
    return false;
}

// Simple peak detection fallback
function simplePeakDetection(profile, findMaxima) {
    Array.getStatistics(profile, min, max, mean, stdDev);
    threshold = mean + (findMaxima ? 1 : -1) * stdDev * 0.5;
    minDistance = 10;
    peaks = newArray(0);
    
    for (i = 1; i < profile.length - 1; i++) {
        if (findMaxima) {
            if (profile[i] > threshold && profile[i] > profile[i-1] && profile[i] > profile[i+1]) {
                if (peaks.length == 0 || i - peaks[peaks.length-1] > minDistance) {
                    peaks = Array.concat(peaks, i);
                }
            }
        } else {
            if (profile[i] < threshold && profile[i] < profile[i-1] && profile[i] < profile[i+1]) {
                if (peaks.length == 0 || i - peaks[peaks.length-1] > minDistance) {
                    peaks = Array.concat(peaks, i);
                }
            }
        }
    }
    return peaks;
}