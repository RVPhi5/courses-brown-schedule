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
                    <span className="legend-title">Enrollment:</span>
                    <div className="legend-items">
                        <div className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: '#e3f2fd' }}></span>
                            <span>1-20</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: '#90caf9' }}></span>
                            <span>21-50</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: '#42a5f5' }}></span>
                            <span>51-100</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: '#1e88e5' }}></span>
                            <span>101-150</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: '#1565c0' }}></span>
                            <span>151-200</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: '#7e57c2' }}></span>
                            <span>201-300</span>
                        </div>
                        <div className="legend-item">
                            <span className="legend-color" style={{ backgroundColor: '#d32f2f' }}></span>
                            <span>300+</span>
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
