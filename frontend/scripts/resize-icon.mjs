import sharp from 'sharp';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(__dirname, '..', 'public');
const src = path.join(publicDir, 'logo.png');
const dest192 = path.join(publicDir, 'logo-192.png');

await sharp(src)
  .resize(192, 192)
  .png()
  .toFile(dest192);
console.log('Created public/logo-192.png (192×192)');
