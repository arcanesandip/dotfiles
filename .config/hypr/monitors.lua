------------------
---- MONITORS ----
------------------

-- See https://wiki.hypr.land/Configuring/Basics/Monitors/
-- Run command in terminal to find your connected monitors: hyprctl monitors all

hl.monitor({
    output = "eDP-1", 
    mode = "1920x1080@120",
    position = "0x0",       -- Placed at the top-left anchor point (acts as the base screen)
    scale = 1.50,
    cm = "hdr",
    bitdepth = 10,
    transform = 0
})

hl.monitor({
    output = "DP-5",    
    mode = "1920x1080@100",
    -- POSITION: Coordinates (X x Y) where screen starts. 
    -- Negative Y (-1080) moves this monitor DIRECTLY ON TOP of the base screen.
    -- Other examples: "1920x0" (to the right), "0x1080" (below), or "auto"
    position = "0x-1080",
    scale = "auto",
    cm = "hdr",
    -- ROTATION/FLIP: 0: normal, 1: 90 deg, 2: 180 deg, 3: 270 deg
    -- 4 through 7 are flipped versions
    transform = 0
})
