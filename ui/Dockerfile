# Use Node 22
FROM node:22

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies (includes Vite)
RUN npm ci

# Copy source code
COPY src/ ./src
COPY vite.config.ts ./
COPY tsconfig.json ./
COPY tailwind.config.js ./

# Expose dev port
EXPOSE 3000

# Start dev server
CMD ["npm", "run", "dev"]
