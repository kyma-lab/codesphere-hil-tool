# Use the official Node.js 16 image as a parent image
FROM node:20

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install project dependencies
RUN npm ci

# Copy the rest of the application code
COPY . .

# Build the Svelte application
RUN npm run build

# Delete source code files that were used to build the app that are no longer needed
RUN rm -rf src/ static/

EXPOSE 3000

# Command to run the application
CMD ["node", "build/index.js"]
