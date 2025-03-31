"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.customerConfigs = void 0;
exports.customerConfigs = [
    {
        id: 'customer1',
        name: 'Acme Corp',
        region: 'us-east-1',
        cameras: [
            {
                id: 'cam1',
                name: 'Main Entrance',
                rtspUrl: 'rtsp://camera1.example.com/stream1',
                streamName: 'acme-main-entrance',
                resolution: {
                    width: 1920,
                    height: 1080
                },
                fps: 30,
                bitrate: 4000,
                location: 'Main Building Entrance',
                description: '24/7 surveillance of main entrance'
            },
            {
                id: 'cam2',
                name: 'Parking Lot',
                rtspUrl: 'rtsp://camera2.example.com/stream1',
                streamName: 'acme-parking-lot',
                resolution: {
                    width: 1920,
                    height: 1080
                },
                fps: 30,
                bitrate: 4000,
                location: 'North Parking Lot',
                description: 'Parking lot surveillance'
            }
        ]
    }
];
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiY3VzdG9tZXItY29uZmlncy5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbIi4uLy4uL2NvbmZpZy9jdXN0b21lci1jb25maWdzLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7OztBQUVhLFFBQUEsZUFBZSxHQUFxQjtJQUMvQztRQUNFLEVBQUUsRUFBRSxXQUFXO1FBQ2YsSUFBSSxFQUFFLFdBQVc7UUFDakIsTUFBTSxFQUFFLFdBQVc7UUFDbkIsT0FBTyxFQUFFO1lBQ1A7Z0JBQ0UsRUFBRSxFQUFFLE1BQU07Z0JBQ1YsSUFBSSxFQUFFLGVBQWU7Z0JBQ3JCLE9BQU8sRUFBRSxvQ0FBb0M7Z0JBQzdDLFVBQVUsRUFBRSxvQkFBb0I7Z0JBQ2hDLFVBQVUsRUFBRTtvQkFDVixLQUFLLEVBQUUsSUFBSTtvQkFDWCxNQUFNLEVBQUUsSUFBSTtpQkFDYjtnQkFDRCxHQUFHLEVBQUUsRUFBRTtnQkFDUCxPQUFPLEVBQUUsSUFBSTtnQkFDYixRQUFRLEVBQUUsd0JBQXdCO2dCQUNsQyxXQUFXLEVBQUUsb0NBQW9DO2FBQ2xEO1lBQ0Q7Z0JBQ0UsRUFBRSxFQUFFLE1BQU07Z0JBQ1YsSUFBSSxFQUFFLGFBQWE7Z0JBQ25CLE9BQU8sRUFBRSxvQ0FBb0M7Z0JBQzdDLFVBQVUsRUFBRSxrQkFBa0I7Z0JBQzlCLFVBQVUsRUFBRTtvQkFDVixLQUFLLEVBQUUsSUFBSTtvQkFDWCxNQUFNLEVBQUUsSUFBSTtpQkFDYjtnQkFDRCxHQUFHLEVBQUUsRUFBRTtnQkFDUCxPQUFPLEVBQUUsSUFBSTtnQkFDYixRQUFRLEVBQUUsbUJBQW1CO2dCQUM3QixXQUFXLEVBQUUsMEJBQTBCO2FBQ3hDO1NBQ0Y7S0FDRjtDQUNGLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgeyBDdXN0b21lckNvbmZpZyB9IGZyb20gJy4vdHlwZXMnO1xyXG5cclxuZXhwb3J0IGNvbnN0IGN1c3RvbWVyQ29uZmlnczogQ3VzdG9tZXJDb25maWdbXSA9IFtcclxuICB7XHJcbiAgICBpZDogJ2N1c3RvbWVyMScsXHJcbiAgICBuYW1lOiAnQWNtZSBDb3JwJyxcclxuICAgIHJlZ2lvbjogJ3VzLWVhc3QtMScsXHJcbiAgICBjYW1lcmFzOiBbXHJcbiAgICAgIHtcclxuICAgICAgICBpZDogJ2NhbTEnLFxyXG4gICAgICAgIG5hbWU6ICdNYWluIEVudHJhbmNlJyxcclxuICAgICAgICBydHNwVXJsOiAncnRzcDovL2NhbWVyYTEuZXhhbXBsZS5jb20vc3RyZWFtMScsXHJcbiAgICAgICAgc3RyZWFtTmFtZTogJ2FjbWUtbWFpbi1lbnRyYW5jZScsXHJcbiAgICAgICAgcmVzb2x1dGlvbjoge1xyXG4gICAgICAgICAgd2lkdGg6IDE5MjAsXHJcbiAgICAgICAgICBoZWlnaHQ6IDEwODBcclxuICAgICAgICB9LFxyXG4gICAgICAgIGZwczogMzAsXHJcbiAgICAgICAgYml0cmF0ZTogNDAwMCxcclxuICAgICAgICBsb2NhdGlvbjogJ01haW4gQnVpbGRpbmcgRW50cmFuY2UnLFxyXG4gICAgICAgIGRlc2NyaXB0aW9uOiAnMjQvNyBzdXJ2ZWlsbGFuY2Ugb2YgbWFpbiBlbnRyYW5jZSdcclxuICAgICAgfSxcclxuICAgICAge1xyXG4gICAgICAgIGlkOiAnY2FtMicsXHJcbiAgICAgICAgbmFtZTogJ1BhcmtpbmcgTG90JyxcclxuICAgICAgICBydHNwVXJsOiAncnRzcDovL2NhbWVyYTIuZXhhbXBsZS5jb20vc3RyZWFtMScsXHJcbiAgICAgICAgc3RyZWFtTmFtZTogJ2FjbWUtcGFya2luZy1sb3QnLFxyXG4gICAgICAgIHJlc29sdXRpb246IHtcclxuICAgICAgICAgIHdpZHRoOiAxOTIwLFxyXG4gICAgICAgICAgaGVpZ2h0OiAxMDgwXHJcbiAgICAgICAgfSxcclxuICAgICAgICBmcHM6IDMwLFxyXG4gICAgICAgIGJpdHJhdGU6IDQwMDAsXHJcbiAgICAgICAgbG9jYXRpb246ICdOb3J0aCBQYXJraW5nIExvdCcsXHJcbiAgICAgICAgZGVzY3JpcHRpb246ICdQYXJraW5nIGxvdCBzdXJ2ZWlsbGFuY2UnXHJcbiAgICAgIH1cclxuICAgIF1cclxuICB9XHJcbl07ICJdfQ==