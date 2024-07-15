#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D textureSampler;
uniform float u_time;    // Time input for general animation (in nanoseconds)
uniform float u_mtime;   // Time input for wave2 animation (in nanoseconds)

// Uniforms to toggle effects
uniform bool u_enableKaleidoscope;
uniform bool u_enableWave;
uniform bool u_enableWave2;      // Toggle for wave2 effect
uniform bool u_enableRandomOffset;
uniform float u_sides;
uniform float u_speed;  // Speed multiplier for wave animations

// A simple pseudo-random function
float random(vec2 co){
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main()
{
    // Initial texture coordinate
    vec2 uv = TexCoord;

    // Apply kaleidoscope effect if enabled
    if (u_enableKaleidoscope) {
        // Kaleidoscope parameters
        float segments = u_sides;  // Number of kaleidoscope segments
        float angle = 2.0 * 3.1416 / segments;
        
        // Calculate kaleidoscope coordinates
        vec2 center = vec2(0.5, 0.5);  // Center of kaleidoscope
        vec2 delta = uv - center;
        float r = length(delta);
        float phi = atan(delta.y, delta.x);
        float segmentAngle = mod(phi, angle);
        float segmentIndex = floor(phi / angle);
        float mirroredPhi = mod(segmentIndex * angle - phi + angle, 2.0 * angle);
        uv = center + vec2(r * cos(mirroredPhi), r * sin(mirroredPhi));
    }
    
    // Apply wave effect if enabled
    if (u_enableWave) {
        float waveAmplitude = 0.1;
        float waveFrequency = 5.0;
        // Calculate wave offset using sine function based on time and speed
        float waveOffset = sin(u_time * u_speed + uv.x * waveFrequency) * waveAmplitude;

        // Apply wave offset to uv.y (vertical wave)
        uv.y += waveOffset;
    }
   
    // Apply wave2 effect if enabled
    if (u_enableWave2) {
        float wave2Amplitude = 0.08;  // Amplitude of the wave2 distortion
        float wave2Frequency = 5.0;   // Frequency of the wave2 distortion
        
        // Convert u_mtime from nanoseconds to seconds
        float mtimeSeconds = u_mtime / 1000000000.0;  // Convert nanoseconds to seconds
        
        // Calculate wave2 offset based on mtimeSeconds and u_speed
        float wave2Offset = mtimeSeconds * u_speed;
        
        uv += vec2(
            wave2Amplitude * sin(wave2Frequency * uv.y + wave2Offset),
            wave2Amplitude * cos(wave2Frequency * uv.x + wave2Offset)
        );
    }
   
    // Apply random offset if enabled
    if (u_enableRandomOffset) {
        float offsetX = (random(uv + u_time) - 0.5) * 0.05;  // Adjust the multiplier for strength of effect
        float offsetY = (random(uv - u_time) - 0.5) * 0.05;  // Adjust the multiplier for strength of effect
        uv += vec2(offsetX, offsetY);
    }

    // Sample the texture and assign to FragColor
    FragColor = texture(textureSampler, uv);
}
