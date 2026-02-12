import { useState, useEffect } from 'react';
import ScheduleGrid from './components/ScheduleGrid';
import { generateTimeSlots, createScheduleGrid } from './utils/scheduleUtils';
import './App.css';

function App() {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [scheduleGrid, setScheduleGrid] = useState(null);
    const [timeSlots, setTimeSlots] = useState([]);

    useEffect(() => {
        // Load course data
        fetch('/schedule_data.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load course data');
                }
                return response.json();
            })
            .then(data => {
                setCourses(data.courses);

                // Generate time slots (8 AM to 10 PM, 30-minute intervals)
                const slots = generateTimeSlots(8, 22, 30);
                setTimeSlots(slots);

                // Create schedule grid
                const grid = createScheduleGrid(data.courses, slots);
                setScheduleGrid(grid);

                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="app-container">
                <div className="loading">Loading course data...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="app-container">
                <div className="error">Error: {error}</div>
            </div>
        );
    }

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>Brown University Course Schedule Heat Map</h1>
                <p className="subtitle">
                    Showing enrollment density across {courses.length} courses
                </p>
                <div className="legend">
                    <span className="legend-title">Enrollment Density:</span>
                    <div className="legend-gradient">
                        <div className="gradient-bar" style={{
                            background: 'linear-gradient(to right, hsl(240, 70%, 85%), hsl(180, 85%, 70%), hsl(120, 92%, 55%), hsl(60, 100%, 50%), hsl(30, 100%, 50%), hsl(0, 100%, 45%))',
                            width: '300px',
                            height: '20px',
                            borderRadius: '4px',
                            border: '1px solid #bdbdbd'
                        }}></div>
                        <div className="gradient-labels" style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            width: '300px',
                            fontSize: '12px',
                            marginTop: '5px'
                        }}>
                            <span>0</span>
                            <span>500</span>
                            <span>1000</span>
                            <span>1500</span>
                            <span>2000</span>
                            <span>2500+</span>
                        </div>
                    </div>
                </div>
            </header>

            {scheduleGrid && (
                <ScheduleGrid scheduleGrid={scheduleGrid} timeSlots={timeSlots} />
            )}
        </div>
    );
}

export default App;
