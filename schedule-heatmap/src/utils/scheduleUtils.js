/**
 * Utility functions for parsing and processing course schedule data
 */

/**
 * Convert time string (HH:MM) to minutes since midnight
 */
export function timeToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
}

/**
 * Convert minutes since midnight to time string (HH:MM)
 */
export function minutesToTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

/**
 * Format time for display (e.g., "14:30" -> "2:30 PM")
 */
export function formatTime(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    const period = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours % 12 || 12;
    return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
}

/**
 * Map day abbreviation to day index (0 = Sunday, 6 = Saturday)
 */
export function dayToIndex(day) {
    const dayMap = {
        'Su': 0,
        'M': 1,
        'T': 2,
        'W': 3,
        'Th': 4,
        'F': 5,
        'S': 6
    };
    return dayMap[day] ?? -1;
}

/**
 * Map day index to full name
 */
export function indexToDayName(index) {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[index] || '';
}

/**
 * Generate time slots for the schedule grid
 * @param {number} startHour - Starting hour (24-hour format)
 * @param {number} endHour - Ending hour (24-hour format)
 * @param {number} intervalMinutes - Interval between slots in minutes
 */
export function generateTimeSlots(startHour = 8, endHour = 22, intervalMinutes = 30) {
    const slots = [];
    const startMinutes = startHour * 60;
    const endMinutes = endHour * 60;

    for (let minutes = startMinutes; minutes < endMinutes; minutes += intervalMinutes) {
        slots.push({
            startMinutes: minutes,
            endMinutes: minutes + intervalMinutes,
            startTime: minutesToTime(minutes),
            endTime: minutesToTime(minutes + intervalMinutes),
            displayTime: formatTime(minutesToTime(minutes))
        });
    }

    return slots;
}

/**
 * Check if a course overlaps with a time slot
 */
export function courseOverlapsSlot(course, slotStartMinutes, slotEndMinutes, dayIndex) {
    // Check if course is on this day
    const courseDayIndices = course.days.map(dayToIndex);
    if (!courseDayIndices.includes(dayIndex)) {
        return false;
    }

    // Check if course time overlaps with slot
    const courseStartMinutes = timeToMinutes(course.start_time);
    const courseEndMinutes = timeToMinutes(course.end_time);

    // Overlap if: course starts before slot ends AND course ends after slot starts
    return courseStartMinutes < slotEndMinutes && courseEndMinutes > slotStartMinutes;
}

/**
 * Get all courses for a specific time slot and day
 */
export function getCoursesForSlot(courses, slotStartMinutes, slotEndMinutes, dayIndex) {
    return courses.filter(course =>
        courseOverlapsSlot(course, slotStartMinutes, slotEndMinutes, dayIndex)
    );
}

/**
 * Calculate total enrollment for a time slot
 */
export function calculateSlotEnrollment(courses, slotStartMinutes, slotEndMinutes, dayIndex) {
    const slotCourses = getCoursesForSlot(courses, slotStartMinutes, slotEndMinutes, dayIndex);
    return slotCourses.reduce((total, course) => total + (course.current_enrollment || 0), 0);
}

/**
 * Get color based on enrollment count using a smooth spectrum
 */
export function getEnrollmentColor(enrollment) {
    if (enrollment === 0) return '#f5f5f5'; // Light gray for empty slots

    // Clamp enrollment to max of 2500
    const normalized = Math.min(enrollment, 2500) / 2500;

    // Create a smooth spectrum: blue -> cyan -> green -> yellow -> orange -> red
    // Using HSL color space for smooth transitions
    // Hue: 240 (blue) -> 0 (red)
    const hue = 240 - (normalized * 240);

    // Saturation: 70-100% (more saturated at higher values)
    const saturation = 70 + (normalized * 30);

    // Lightness: 85% (light) -> 45% (dark) for better contrast
    const lightness = 85 - (normalized * 40);

    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

/**
 * Process all courses and create a grid data structure
 */
export function createScheduleGrid(courses, timeSlots) {
    const grid = {};

    // Initialize grid for each day
    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
        grid[dayIndex] = timeSlots.map(slot => ({
            ...slot,
            dayIndex,
            courses: getCoursesForSlot(courses, slot.startMinutes, slot.endMinutes, dayIndex),
            enrollment: calculateSlotEnrollment(courses, slot.startMinutes, slot.endMinutes, dayIndex)
        }));
    }

    return grid;
}
