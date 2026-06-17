var asteroidDiameter = {
    initialized: false,
    canvas: null,
    ctx: null,
    containerWidth: 0,
    containerHeight: 0,
    diameterMin: 0,
    diameterMax: 0,
    scale: 0.3, // pixels per meter

    init: function(containerId, diameterMin, diameterMax) {
        
        if (!diameterMin || !diameterMax) {
            console.warn('[asteroidDiameter] Missing diameter values');
            return;
        }

        var container = genro.dom.getDomNode(containerId);
        if (!container) {
            console.warn('[asteroidDiameter] container not found:', containerId);
            return;
        }

        asteroidDiameter.diameterMin = diameterMin;
        asteroidDiameter.diameterMax = diameterMax;
        asteroidDiameter.containerWidth = container.clientWidth || 1120;
        asteroidDiameter.containerHeight = container.clientHeight || 380;

        // Create canvas element
        asteroidDiameter.canvas = document.createElement('canvas');
        asteroidDiameter.canvas.width = asteroidDiameter.containerWidth;
        asteroidDiameter.canvas.height = asteroidDiameter.containerHeight;
        asteroidDiameter.canvas.style.display = 'block';
        
        // Clear the container and add canvas
        container.innerHTML = '';
        container.appendChild(asteroidDiameter.canvas);
        asteroidDiameter.ctx = asteroidDiameter.canvas.getContext('2d');

        // Calculate scale: fit the largest diameter with some padding
        var maxDiameter = diameterMax;
        var padding = 150; // pixels for scale ruler
        var availableWidth = asteroidDiameter.containerWidth - padding - 20;
        var availableHeight = asteroidDiameter.containerHeight - 40;
        
        asteroidDiameter.scale = Math.min(
            availableWidth / maxDiameter,
            availableHeight / maxDiameter
        );

        asteroidDiameter._draw();
        asteroidDiameter.initialized = true;

        // Handle window resize
        window.addEventListener('resize', function() {
            var newW = container.clientWidth;
            var newH = container.clientHeight;
            if (newW !== asteroidDiameter.containerWidth || 
                newH !== asteroidDiameter.containerHeight) {
                asteroidDiameter.containerWidth = newW;
                asteroidDiameter.containerHeight = newH;
                asteroidDiameter.canvas.width = newW;
                asteroidDiameter.canvas.height = newH;
                asteroidDiameter._draw();
            }
        });
    },

    _draw: function() {
        var ctx = asteroidDiameter.ctx;
        var w = asteroidDiameter.containerWidth;
        var h = asteroidDiameter.containerHeight;
        var scale = asteroidDiameter.scale;
        var dMin = asteroidDiameter.diameterMin;
        var dMax = asteroidDiameter.diameterMax;

        // Clear canvas
        ctx.fillStyle = '#000010';
        ctx.fillRect(0, 0, w, h);

        // Center point (left of scale ruler)
        var centerX = (w - 80) / 2 + 20;
        var centerY = h / 2;

        // Draw max diameter circle (50% opacity)
        ctx.strokeStyle = 'rgba(51, 153, 255, 0.5)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, (dMax / 2) * scale, 0, 2 * Math.PI);
        ctx.stroke();

        // Draw min diameter circle (solid/100% opacity)
        ctx.strokeStyle = 'rgba(51, 153, 255, 1.0)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, (dMin / 2) * scale, 0, 2 * Math.PI);
        ctx.stroke();

        // Draw diameter lines for both circles
        ctx.strokeStyle = 'rgba(200, 200, 200, 0.3)';
        ctx.setLineDash([5, 5]);
        ctx.lineWidth = 1;

        // Max diameter line
        ctx.beginPath();
        ctx.moveTo(centerX - (dMax / 2) * scale, centerY);
        ctx.lineTo(centerX + (dMax / 2) * scale, centerY);
        ctx.stroke();

        // Min diameter line
        ctx.strokeStyle = 'rgba(200, 200, 200, 0.5)';
        ctx.beginPath();
        ctx.moveTo(centerX - (dMin / 2) * scale, centerY);
        ctx.lineTo(centerX + (dMin / 2) * scale, centerY);
        ctx.stroke();

        ctx.setLineDash([]);

        // Draw scale ruler on the right
        asteroidDiameter._drawScaleRuler(centerX + 40, centerY, scale, dMax);

        // Draw labels
        ctx.fillStyle = '#CCCCCC';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';

        // Min diameter label
        ctx.fillText('Min: ' + dMin.toFixed(2) + ' m', centerX, centerY - (dMin / 2) * scale - 15);

        // Max diameter label
        ctx.fillStyle = 'rgba(200, 200, 200, 0.7)';
        ctx.fillText('Max: ' + dMax.toFixed(2) + ' m', centerX, -centerY + (dMax / 2) * scale + 75);
    },

    _drawScaleRuler: function(x, y, scale, maxDiameter) {
        var ctx = asteroidDiameter.ctx;
        var outSide = maxDiameter/2*scale
        // Ruler background
        //ctx.fillStyle = 'rgba(30, 30, 30, 0.8)';
        //ctx.fillRect(x - 5, y - (maxDiameter / 2) * scale - 5, 50, (maxDiameter * scale) + 10);

        // Ruler border
        //ctx.strokeStyle = 'rgba(100, 100, 100, 0.5)';
        //ctx.lineWidth = 1;
        //ctx.strokeRect(x - 5, y - (maxDiameter / 2) * scale - 5, 50, (maxDiameter * scale) + 10);

        // Draw tick marks and labels
        var rulerLength = (maxDiameter / 2) * scale;
        var tickInterval = asteroidDiameter._getTickInterval(maxDiameter);
        var pixelsPerMeter = scale;
        var x = x+outSide
        for (var i = 0; i <= maxDiameter; i += tickInterval) {
            var pixelPos = (i / 2) * pixelsPerMeter;
            
            // Top tick
            ctx.strokeStyle = 'rgba(150, 150, 150, 0.7)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x - 3, y - pixelPos);
            ctx.lineTo(x + 2, y - pixelPos);
            ctx.stroke();

            // Bottom tick
            ctx.beginPath();
            ctx.moveTo(x - 3, y + pixelPos);
            ctx.lineTo(x + 2, y + pixelPos);
            ctx.stroke();

            // Label every other tick
            if (i % (tickInterval * 2) === 0) {
                ctx.fillStyle = 'rgba(150, 200, 255, 0.8)';
                ctx.font = 'bold 10px Arial';
                ctx.textAlign = 'left';
                var label = i.toFixed(0);
                ctx.fillText(label+' m', x + 8, y - pixelPos + 3);
            }
        }

        // Unit label
        ctx.fillStyle = 'rgba(150, 150, 150, 0.7)';
        ctx.font = '9px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('(m)', x + outSide + 17, y + (maxDiameter / 2) * scale + 20);
    },

    _getTickInterval: function(maxDiameter) {
        // Auto-select nice tick interval
        if (maxDiameter <= 10) return 1;
        if (maxDiameter <= 50) return 5;
        if (maxDiameter <= 100) return 10;
        if (maxDiameter <= 500) return 50;
        if (maxDiameter <= 1000) return 100;
        return 500;
    }
};
