# Job Board Assistant

A simple, beautiful Kanban-style job application tracker built with React, TypeScript, and Tailwind CSS. All data is stored locally in your browser using localStorage.

![Job Board Assistant](https://via.placeholder.com/800x400?text=Job+Board+Assistant)

## Features

### 🎯 Kanban Board
- **6 columns** to track your job applications:
  - **Wishlist** - Jobs you're interested in
  - **Applied** - Applications you've submitted
  - **Interview** - Jobs in the interview process
  - **Offer** - Jobs with offers received
  - **Rejected** - Applications that didn't work out
  - **Accepted** - Jobs you've accepted!

### 📊 Dashboard Statistics
- Total jobs in your pipeline
- Applications sent
- Interviews in progress
- Offers received
- Response rate & conversion rate
- Weekly and monthly tracking

### 📝 Job Details
For each job application, you can track:
- **Company Name** & **Job Title**
- **Job URL** - Link to the job posting
- **Source** - Where you found the job (LinkedIn, Indeed, Referral, etc.)
- **Resume Used** - Which resume version you submitted
- **Cover Letter** - Which cover letter you used
- **Status** - Current stage in the process
- **Date Applied** - When you submitted the application
- **Salary Range** - Expected compensation
- **Location** - Job location
- **Work Type** - Remote, Hybrid, or On-site
- **Notes** - Any additional information
- **Updates** - Track progress updates over time

### ✨ Additional Features
- **Drag & Drop** - Move jobs between columns easily
- **Search** - Find jobs by company, title, or location
- **Filter** - Filter by status
- **Export/Import** - Backup your data as JSON
- **Persistent Storage** - All data saved to browser's localStorage

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Navigate to the project directory
cd job-board-assistant

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage Guide

### Adding a New Job
1. Click the **"Add Job"** button in the top right
2. Fill in the job details:
   - Required: Company Name, Job Title, Source, Resume Used
   - Optional: Job URL, Cover Letter, Salary, Location, etc.
3. Select the appropriate status
4. Click **"Add Job"** to save

### Moving Jobs Between Columns
- **Drag and drop** cards between columns
- Or click on a job to edit and change its status

### Adding Updates
1. Click on any job card to open the edit modal
2. Switch to the **"Updates"** tab
3. Enter your update (e.g., "Phone screen scheduled for next week")
4. Click **"Add"** to save the update

### Searching and Filtering
- Use the **search bar** to find jobs by company, title, or location
- Use the **filter dropdown** to show only jobs in a specific status

### Backing Up Your Data
- Click the **download icon** to export all your data as a JSON file
- Click the **upload icon** to import a previously exported JSON file

## Data Storage

All your job application data is stored in your browser's **localStorage**. This means:
- ✅ Your data persists between browser sessions
- ✅ No server or database needed - runs entirely locally
- ⚠️ Data is tied to this browser on this device
- ⚠️ Clearing browser data will delete your job applications

**Recommendation:** Regularly export your data as a backup!

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS 4** - Styling
- **@hello-pangea/dnd** - Drag and drop functionality
- **Lucide React** - Icons
- **localStorage** - Data persistence

## Customization

### Changing Column Colors
Edit the `COLUMNS` array in `src/types/index.ts`:

```typescript
export const COLUMNS: Column[] = [
  { id: 'wishlist', title: 'Wishlist', color: '#94a3b8' },
  { id: 'applied', title: 'Applied', color: '#3b82f6' },
  // ... change the color values
];
```

### Adding New Job Sources
Edit the source options in `src/components/JobModal.tsx`:

```typescript
<select ...>
  <option value="LinkedIn">LinkedIn</option>
  <option value="Indeed">Indeed</option>
  {/* Add your custom source here */}
</select>
```

## License

MIT License - feel free to use this for your job search!

## Tips for Job Searching

1. **Update regularly** - Keep your board current by moving jobs as they progress
2. **Track everything** - Even rejections are useful data for your response rate
3. **Use updates** - Log every interaction to remember details later
4. **Note which resume works** - Track which resume versions get responses
5. **Follow up** - Use the updates to remind yourself when to follow up

Good luck with your job search! 🚀
