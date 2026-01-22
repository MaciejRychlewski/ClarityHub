let globalData = [];
// State for the calendar
let currentCalendarDate = new Date();

document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 Clarity Hub Frontend Loaded");
    updateClock();
    setInterval(updateClock, 1000);
    loadNotifications();

    // Connect Listeners
    connectClick('box-calendar', window.toggleCalendar);
    connectClick('box-urgent', () => window.openListModal('urgent'));
    connectClick('box-important', () => window.openListModal('important'));
    connectClick('box-stream', () => window.openListModal('stream'));
    connectClick('box-favourites', () => window.openListModal('favourites'));
});

function connectClick(id, action) {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', action);
}

// === CALENDAR LOGIC ===

window.changeMonth = function(offset) {
    // Move month forward or backward
    currentCalendarDate.setMonth(currentCalendarDate.getMonth() + offset);
    renderFullCalendar(); // Re-render with new date
}

window.renderFullCalendar = function() {
    const grid = document.getElementById('calendar-grid');
    const header = document.getElementById('calendar-header-date');
    if(!grid || !header) return;

    // Update Header (e.g., "FEBRUARY 2026")
    header.innerText = currentCalendarDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

    grid.innerHTML = ''; 

    // Calculate Month Details
    const year = currentCalendarDate.getFullYear();
    const month = currentCalendarDate.getMonth();
    
    // First day of the month (0 = Sunday, 1 = Monday)
    const firstDay = new Date(year, month, 1).getDay();
    // Adjust so Monday is 0 (European/Business style)
    const startOffset = firstDay === 0 ? 6 : firstDay - 1;
    
    // Days in this month
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // 1. Empty slots for previous month
    for(let i = 0; i < startOffset; i++) {
        grid.innerHTML += `<div class="p-2"></div>`;
    }

    // 2. Days of the current month
    const today = new Date();
    const isCurrentMonth = today.getMonth() === month && today.getFullYear() === year;

    for (let day = 1; day <= daysInMonth; day++) {
        const isToday = isCurrentMonth && day === today.getDate();
        
        // Random events (deterministic based on day number so they don't change when switching months)
        const hasEvent = (day + month) % 3 === 0; 
        
        let dayContent = `<span class="${isToday ? 'text-white font-bold bg-purple-500 w-6 h-6 rounded-full flex items-center justify-center shadow-lg shadow-purple-500/50' : 'text-gray-400'}">${day}</span>`;
        
        if (hasEvent) {
            const events = ["Client Call", "Team Sync", "Deep Work", "Review", "Deadline"];
            const randomTitle = events[(day + month) % events.length];
            dayContent += `
                <div class="mt-2 w-full bg-purple-500/10 border-l-2 border-purple-500 p-1 rounded-r text-[8px] text-purple-200 truncate group-hover:bg-purple-500/20 transition">
                    ${randomTitle}
                </div>
            `;
        }

        grid.innerHTML += `
            <div class="bg-white/5 border border-white/5 rounded-xl p-2 flex flex-col hover:bg-white/10 transition min-h-[80px] group">
                ${dayContent}
            </div>
        `;
    }
}

// === STANDARD MODALS ===

window.toggleCalendar = function() {
    toggleModal('calendar-modal', 'calendar-content', () => {
        currentCalendarDate = new Date(); // Reset to today when opening
        renderFullCalendar();
    });
}

window.toggleListModal = function() {
    toggleModal('list-modal', 'list-content', null);
}

window.openListModal = function(type) {
    const titleEl = document.getElementById('modal-title');
    const listContainer = document.getElementById('modal-list-container');
    let items = [];
    let color = '';
    let icon = '';

    if (type === 'urgent') {
        items = globalData.filter(n => n.priority === 'urgent');
        color = 'red';
        icon = '<i class="fa-solid fa-triangle-exclamation"></i>';
        titleEl.innerHTML = `${icon} <span class="text-red-400">URGENT ALERTS</span>`;
    } else if (type === 'important') {
        items = globalData.filter(n => n.priority === 'high');
        color = 'blue';
        icon = '<i class="fa-solid fa-circle-exclamation"></i>';
        titleEl.innerHTML = `${icon} <span class="text-blue-400">IMPORTANT ITEMS</span>`;
    } else if (type === 'stream') {
        items = globalData; 
        color = 'green';
        icon = '<i class="fa-solid fa-tower-broadcast"></i>';
        titleEl.innerHTML = `${icon} <span class="text-green-400">FULL STREAM</span>`;
    } else if (type === 'favourites') {
        items = globalData.slice(0, 5);
        color = 'yellow';
        icon = '<i class="fa-solid fa-star"></i>';
        titleEl.innerHTML = `${icon} <span class="text-yellow-400">FAVOURITES</span>`;
    }

    if (type === 'stream') {
        renderStream(listContainer.id, items); 
    } else {
        renderList(listContainer.id, items, color); 
    }
    toggleModal('list-modal', 'list-content', null);
}

// === CORE RENDERERS ===

async function loadNotifications() {
    try {
        const response = await fetch(`../notifications.json?t=${new Date().getTime()}`);
        globalData = await response.json(); 

        const urgentItems = globalData.filter(n => n.priority === 'urgent');
        renderList('urgent-container', urgentItems, 'red');

        const highItems = globalData.filter(n => n.priority === 'high');
        renderList('important-container', highItems, 'blue');

        const calendarItems = globalData.filter(n => n.source === 'calendar');
        renderList('calendar-container', calendarItems, 'purple');

        renderStream('all-stream-container', globalData);

        const favItems = globalData.slice(0, 2); 
        renderList('favourites-container', favItems, 'yellow');

    } catch (error) { console.error(error); }
}

function renderList(containerId, items, colorTheme) {
    const container = document.getElementById(containerId);
    if (!container) return;
    if (items.length === 0) {
        container.innerHTML = `<div class="text-gray-600 italic text-[10px]">No items</div>`;
        return;
    }
    container.innerHTML = items.map(item => `
        <div class="bg-white/5 border border-white/5 p-3 rounded-xl mb-2 hover:bg-white/10 transition group">
            <div class="flex justify-between items-start mb-1">
                <span class="text-${colorTheme}-400 text-[10px] font-bold uppercase tracking-wider">${item.source}</span>
                <span class="text-gray-500 text-[10px]">${formatTime(item.timestamp)}</span>
            </div>
            <h4 class="text-gray-200 text-sm font-medium leading-tight group-hover:text-${colorTheme}-300 transition">${item.title}</h4>
        </div>
    `).join('');
}

function renderStream(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = items.map(item => `
        <div class="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition border border-transparent hover:border-white/5 group">
            <div class="w-10 h-10 rounded-lg bg-gray-800/50 flex items-center justify-center border border-white/5 group-hover:scale-110 transition duration-300">
                ${getSourceIcon(item.source)}
            </div>
            <div class="flex-1 min-w-0">
                <div class="flex justify-between">
                    <h4 class="text-sm font-medium text-gray-200 truncate pr-4">${item.title}</h4>
                    <span class="text-[10px] text-gray-500 whitespace-nowrap">${formatTime(item.timestamp)}</span>
                </div>
                <p class="text-[11px] text-gray-500 truncate mt-0.5">${item.content}</p>
            </div>
            ${getPriorityBadge(item.priority)}
        </div>
    `).join('');
}

// === HELPERS ===
function updateClock() {
    const now = new Date();
    const timeEl = document.getElementById('clock-time');
    const dateEl = document.getElementById('clock-date');
    if(timeEl) timeEl.innerText = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    if(dateEl) dateEl.innerText = now.toLocaleDateString([], {weekday: 'long', month: 'short', day: 'numeric'});
}

function toggleModal(modalId, contentId, renderCallback) {
    const modal = document.getElementById(modalId);
    const content = document.getElementById(contentId);
    if (!modal) return;
    if (modal.classList.contains('hidden')) {
        if(renderCallback) renderCallback(); 
        modal.classList.remove('hidden');
        setTimeout(() => { modal.classList.remove('opacity-0'); content.classList.remove('scale-95'); content.classList.add('scale-100'); }, 10);
    } else {
        modal.classList.add('opacity-0'); content.classList.remove('scale-100'); content.classList.add('scale-95');
        setTimeout(() => { modal.classList.add('hidden'); }, 300);
    }
}

function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInSeconds < 60) return `<span class="text-green-400 font-bold">Just now</span>`;
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${diffInDays}d ago`;
}

function getSourceIcon(source) {
    const map = { 'slack': '<i class="fa-brands fa-slack text-purple-400"></i>', 'gmail': '<i class="fa-brands fa-google text-red-400"></i>', 'discord': '<i class="fa-brands fa-discord text-indigo-400"></i>', 'calendar': '<i class="fa-regular fa-calendar text-blue-400"></i>', 'github': '<i class="fa-brands fa-github text-white"></i>', 'jira': '<i class="fa-brands fa-jira text-blue-500"></i>' };
    return map[source] || '<i class="fa-solid fa-circle text-gray-500"></i>';
}

function getPriorityBadge(priority) {
    if (priority === 'urgent') return `<span class="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]"></span>`;
    if (priority === 'high') return `<span class="w-2 h-2 rounded-full bg-blue-500"></span>`;
    return '';
}