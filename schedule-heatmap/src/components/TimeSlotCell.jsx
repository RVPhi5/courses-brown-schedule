import PropTypes from 'prop-types';
import { getEnrollmentColor } from '../utils/scheduleUtils';
import './TimeSlotCell.css';

function TimeSlotCell({ slot, dayIndex, slotIndex, onClick, isActive }) {
    const handleClick = (e) => {
        onClick(slot, dayIndex, slotIndex, e.currentTarget);
    };

    const backgroundColor = getEnrollmentColor(slot.enrollment);
    const hasContent = slot.courses.length > 0;

    return (
        <div
            className={`time-slot-cell ${hasContent ? 'has-content' : ''} ${isActive ? 'active' : ''}`}
            style={{ backgroundColor, cursor: hasContent ? 'pointer' : 'default' }}
            onClick={handleClick}
            title={hasContent ? `${slot.courses.length} course(s), ${slot.enrollment} students - Click to view details` : 'No classes'}
        >
            {slot.enrollment > 0 && (
                <span className="enrollment-count">{slot.enrollment}</span>
            )}
        </div>
    );
}

TimeSlotCell.propTypes = {
    slot: PropTypes.shape({
        courses: PropTypes.array.isRequired,
        enrollment: PropTypes.number.isRequired,
    }).isRequired,
    dayIndex: PropTypes.number.isRequired,
    slotIndex: PropTypes.number.isRequired,
    onClick: PropTypes.func.isRequired,
    isActive: PropTypes.bool.isRequired,
};

export default TimeSlotCell;
