# Web Game Architecture

Guidelines for building web games at ButtsStudios.

## Technology Stack

- **HTML5 Canvas** or **WebGL** for rendering
- **JavaScript/TypeScript** for game logic
- **CSS3** for UI and styling

## Game Types

### 2D Games
- Canvas-based rendering
- Sprite-based animations
- Tile-based maps

### 3D Games
- Three.js or raw WebGL
- GLTF models
- PBR materials

## Performance Targets

- 60 FPS on modern browsers
- < 3 second initial load
- Mobile-friendly (touch controls)

## File Structure

```
games/<game-name>/
├── src/
│   ├── index.js      # Entry point
│   ├── game.js       # Main game loop
│   ├── entities/     # Game objects
│   ├── systems/       # Game systems (physics, rendering)
│   └── assets/        # Images, audio
├── public/
│   └── index.html
└── package.json
```

## Best Practices

- Use requestAnimationFrame for game loop
- Object pooling for frequently created objects
- Delta time for frame-independent movement
- Compress assets (WebP, audio)
