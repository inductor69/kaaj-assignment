FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the public directory first
COPY public/ public/

# Copy the src directory
COPY src/ src/

# Copy any other necessary files
COPY tsconfig.json ./
COPY .env* ./

# Build the application
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "build", "-l", "3000"]
