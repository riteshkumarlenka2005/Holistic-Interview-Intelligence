/**
 * Simple local storage based CRUD service
 * Replaces the Wix CMS service with local storage
 */

export interface PaginationOptions {
  limit?: number;
  skip?: number;
}

export interface PaginatedResult<T> {
  items: T[];
  totalCount: number;
  hasNext: boolean;
  currentPage: number;
  pageSize: number;
  nextSkip: number | null;
}

export interface WixDataItem {
  _id: string;
  _createdDate?: Date;
  _updatedDate?: Date;
}

const STORAGE_PREFIX = 'cms_';

export class BaseCrudService {
  /**
   * Get all items from a collection with pagination and optional filtering
   */
  static async getAll<T extends WixDataItem>(
    collectionId: string,
    queryOptions?: Record<string, unknown>,
    pagination?: PaginationOptions
  ): Promise<PaginatedResult<T>> {
    const limit = pagination?.limit || 50;
    const skip = pagination?.skip || 0;

    try {
      const stored = localStorage.getItem(`${STORAGE_PREFIX}${collectionId}`);
      let allItems: T[] = stored ? JSON.parse(stored) : [];



      // Apply filters from queryOptions
      if (queryOptions && Object.keys(queryOptions).length > 0) {
        allItems = allItems.filter((item) => {
          return Object.entries(queryOptions).every(([key, value]) => {
            const itemValue = (item as Record<string, unknown>)[key];
            // Case-insensitive string comparison
            if (typeof itemValue === 'string' && typeof value === 'string') {
              return itemValue.toLowerCase() === value.toLowerCase();
            }
            return itemValue === value;
          });
        });
      }



      const paginatedItems = allItems.slice(skip, skip + limit);
      const hasNext = skip + limit < allItems.length;

      return {
        items: paginatedItems,
        totalCount: allItems.length,
        hasNext,
        currentPage: Math.floor(skip / limit),
        pageSize: limit,
        nextSkip: hasNext ? skip + limit : null,
      };
    } catch (error) {
      console.error(`Error getting items from ${collectionId}:`, error);
      return {
        items: [],
        totalCount: 0,
        hasNext: false,
        currentPage: 0,
        pageSize: limit,
        nextSkip: null,
      };
    }
  }

  /**
   * Get a single item by ID
   */
  static async getById<T extends WixDataItem>(
    collectionId: string,
    itemId: string
  ): Promise<T | null> {
    try {
      const stored = localStorage.getItem(`${STORAGE_PREFIX}${collectionId}`);
      const allItems: T[] = stored ? JSON.parse(stored) : [];
      return allItems.find(item => item._id === itemId) || null;
    } catch (error) {
      console.error(`Error getting item ${itemId} from ${collectionId}:`, error);
      return null;
    }
  }

  /**
   * Create a new item
   */
  static async create<T extends WixDataItem>(
    collectionId: string,
    itemData: Partial<T> | Record<string, unknown>
  ): Promise<T> {
    try {
      const stored = localStorage.getItem(`${STORAGE_PREFIX}${collectionId}`);
      const allItems: T[] = stored ? JSON.parse(stored) : [];

      const newItem = {
        ...itemData,
        _id: itemData._id || crypto.randomUUID(),
        _createdDate: new Date(),
        _updatedDate: new Date(),
      } as T;

      allItems.push(newItem);
      localStorage.setItem(`${STORAGE_PREFIX}${collectionId}`, JSON.stringify(allItems));

      return newItem;
    } catch (error) {
      console.error(`Error creating item in ${collectionId}:`, error);
      throw error;
    }
  }

  /**
   * Update an existing item
   */
  static async update<T extends WixDataItem>(
    collectionId: string,
    itemId: string,
    itemData: Partial<T>
  ): Promise<T> {
    try {
      const stored = localStorage.getItem(`${STORAGE_PREFIX}${collectionId}`);
      const allItems: T[] = stored ? JSON.parse(stored) : [];

      const index = allItems.findIndex(item => item._id === itemId);
      if (index === -1) {
        throw new Error(`Item ${itemId} not found in ${collectionId}`);
      }

      const updatedItem = {
        ...allItems[index],
        ...itemData,
        _updatedDate: new Date(),
      } as T;

      allItems[index] = updatedItem;
      localStorage.setItem(`${STORAGE_PREFIX}${collectionId}`, JSON.stringify(allItems));

      return updatedItem;
    } catch (error) {
      console.error(`Error updating item ${itemId} in ${collectionId}:`, error);
      throw error;
    }
  }

  /**
   * Delete an item
   */
  static async delete(
    collectionId: string,
    itemId: string
  ): Promise<void> {
    try {
      const stored = localStorage.getItem(`${STORAGE_PREFIX}${collectionId}`);
      const allItems = stored ? JSON.parse(stored) : [];

      const filteredItems = allItems.filter((item: WixDataItem) => item._id !== itemId);
      localStorage.setItem(`${STORAGE_PREFIX}${collectionId}`, JSON.stringify(filteredItems));
    } catch (error) {
      console.error(`Error deleting item ${itemId} from ${collectionId}:`, error);
      throw error;
    }
  }
}
