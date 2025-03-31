"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.systemConfig = void 0;
exports.systemConfig = {
    defaultInstanceType: 't3.medium',
    maxCamerasPerInstance: 10,
    instanceTypes: {
        't3.small': {
            vcpus: 2,
            memoryGiB: 2,
            maxCameras: 5
        },
        't3.medium': {
            vcpus: 2,
            memoryGiB: 4,
            maxCameras: 10
        },
        't3.large': {
            vcpus: 2,
            memoryGiB: 8,
            maxCameras: 20
        },
        't3.xlarge': {
            vcpus: 4,
            memoryGiB: 16,
            maxCameras: 40
        }
    }
};
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoic3lzdGVtLWNvbmZpZy5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbIi4uLy4uL2NvbmZpZy9zeXN0ZW0tY29uZmlnLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7OztBQUVhLFFBQUEsWUFBWSxHQUFpQjtJQUN4QyxtQkFBbUIsRUFBRSxXQUFXO0lBQ2hDLHFCQUFxQixFQUFFLEVBQUU7SUFDekIsYUFBYSxFQUFFO1FBQ2IsVUFBVSxFQUFFO1lBQ1YsS0FBSyxFQUFFLENBQUM7WUFDUixTQUFTLEVBQUUsQ0FBQztZQUNaLFVBQVUsRUFBRSxDQUFDO1NBQ2Q7UUFDRCxXQUFXLEVBQUU7WUFDWCxLQUFLLEVBQUUsQ0FBQztZQUNSLFNBQVMsRUFBRSxDQUFDO1lBQ1osVUFBVSxFQUFFLEVBQUU7U0FDZjtRQUNELFVBQVUsRUFBRTtZQUNWLEtBQUssRUFBRSxDQUFDO1lBQ1IsU0FBUyxFQUFFLENBQUM7WUFDWixVQUFVLEVBQUUsRUFBRTtTQUNmO1FBQ0QsV0FBVyxFQUFFO1lBQ1gsS0FBSyxFQUFFLENBQUM7WUFDUixTQUFTLEVBQUUsRUFBRTtZQUNiLFVBQVUsRUFBRSxFQUFFO1NBQ2Y7S0FDRjtDQUNGLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyBTeXN0ZW1Db25maWcgfSBmcm9tICcuL3R5cGVzJztcclxuXHJcbmV4cG9ydCBjb25zdCBzeXN0ZW1Db25maWc6IFN5c3RlbUNvbmZpZyA9IHtcclxuICBkZWZhdWx0SW5zdGFuY2VUeXBlOiAndDMubWVkaXVtJyxcclxuICBtYXhDYW1lcmFzUGVySW5zdGFuY2U6IDEwLFxyXG4gIGluc3RhbmNlVHlwZXM6IHtcclxuICAgICd0My5zbWFsbCc6IHtcclxuICAgICAgdmNwdXM6IDIsXHJcbiAgICAgIG1lbW9yeUdpQjogMixcclxuICAgICAgbWF4Q2FtZXJhczogNVxyXG4gICAgfSxcclxuICAgICd0My5tZWRpdW0nOiB7XHJcbiAgICAgIHZjcHVzOiAyLFxyXG4gICAgICBtZW1vcnlHaUI6IDQsXHJcbiAgICAgIG1heENhbWVyYXM6IDEwXHJcbiAgICB9LFxyXG4gICAgJ3QzLmxhcmdlJzoge1xyXG4gICAgICB2Y3B1czogMixcclxuICAgICAgbWVtb3J5R2lCOiA4LFxyXG4gICAgICBtYXhDYW1lcmFzOiAyMFxyXG4gICAgfSxcclxuICAgICd0My54bGFyZ2UnOiB7XHJcbiAgICAgIHZjcHVzOiA0LFxyXG4gICAgICBtZW1vcnlHaUI6IDE2LFxyXG4gICAgICBtYXhDYW1lcmFzOiA0MFxyXG4gICAgfVxyXG4gIH1cclxufTsgIl19