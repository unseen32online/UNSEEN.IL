// Mock data for UNSEEN clothing brand

export const mockProducts = [
  // TOPS
  {
    id: 'top-1',
    name: 'Essential Cotton Tee',
    category: 'tops',
    price: 45,
    description: 'Premium cotton tee with a relaxed fit. Perfect for everyday wear.',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Black', 'White', 'Gray'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'top-2',
    name: 'Classic Oxford Shirt',
    category: 'tops',
    price: 89,
    description: 'Timeless oxford shirt crafted from premium cotton. Versatile and comfortable.',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['White', 'Blue', 'Navy'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'top-3',
    name: 'Relaxed Henley',
    category: 'tops',
    price: 65,
    description: 'Casual henley with a comfortable relaxed fit. Effortlessly stylish.',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Olive', 'Navy', 'Charcoal'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'top-4',
    name: 'Lightweight Crewneck',
    category: 'tops',
    price: 55,
    description: 'Soft crewneck perfect for layering or wearing solo.',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Cream', 'Black', 'Sage'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'top-5',
    name: 'Oversized Pocket Tee',
    category: 'tops',
    price: 52,
    description: 'Contemporary oversized fit with chest pocket detail.',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Sand', 'Black', 'White'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'top-6',
    name: 'Long Sleeve Polo',
    category: 'tops',
    price: 78,
    description: 'Refined polo with long sleeves. Perfect for smart-casual occasions.',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Navy', 'Forest', 'Charcoal'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  
  // PANTS
  {
    id: 'pant-1',
    name: 'Tailored Chinos',
    category: 'pants',
    price: 95,
    description: 'Classic chinos with a modern tailored fit. Versatile for any occasion.',
    sizes: ['28', '30', '32', '34', '36'],
    colors: ['Khaki', 'Navy', 'Olive'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'pant-2',
    name: 'Relaxed Fit Denim',
    category: 'pants',
    price: 115,
    description: 'Premium denim with a comfortable relaxed fit. Timeless style.',
    sizes: ['28', '30', '32', '34', '36'],
    colors: ['Indigo', 'Black', 'Light Wash'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'pant-3',
    name: 'Wide Leg Trousers',
    category: 'pants',
    price: 125,
    description: 'Contemporary wide leg trousers with a sophisticated drape.',
    sizes: ['28', '30', '32', '34', '36'],
    colors: ['Charcoal', 'Cream', 'Black'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'pant-4',
    name: 'Cargo Pants',
    category: 'pants',
    price: 98,
    description: 'Modern cargo pants with functional pockets and comfortable fit.',
    sizes: ['28', '30', '32', '34', '36'],
    colors: ['Olive', 'Black', 'Tan'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'pant-5',
    name: 'Drawstring Joggers',
    category: 'pants',
    price: 85,
    description: 'Comfortable joggers with an elevated design. Perfect for casual days.',
    sizes: ['S', 'M', 'L', 'XL'],
    colors: ['Gray', 'Black', 'Navy'],
    image: '',
    images: ['', '', ''],
    inStock: true
  },
  {
    id: 'pant-6',
    name: 'Slim Fit Trousers',
    category: 'pants',
    price: 105,
    description: 'Refined slim fit trousers for a polished look.',
    sizes: ['28', '30', '32', '34', '36'],
    colors: ['Navy', 'Charcoal', 'Tan'],
    image: '',
    images: ['', '', ''],
    inStock: true
  }
];

export const getProductsByCategory = (category) => {
  return mockProducts.filter(product => product.category === category);
};

export const getProductById = (id) => {
  return mockProducts.find(product => product.id === id);
};
